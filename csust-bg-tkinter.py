'''

    22点18分:   加入bg可用性检查
                加入扩展账号功能, 并使用base64编解码
    20点48分: 重连时间2s-3s
    2022年6月21日14点54分: 去除重复检查(前置ping), 进一步优化重连耗时
    2022年6月20日10点51分: 优化提示, 新增提示说明框; 测试ReconnWifi-3s
    2022年6月19日12点10分: 优化状态显示, 精确到1s级
    2022年6月18日11点42分: 12小时测试重连稳定 (未触发paraerr, 待测
'''
import tkinter,threading,time,base64
from tkinter import messagebox

from util import *
from logoData import logodata

MODE = 1
MODE_DES = ['',"常规模式","快速模式"]

def getInfo():    
    print("getinfo")
    confPath = ".config"
    
    if os.path.exists(confPath):
        with open(confPath,'r') as f:
            dc = str(base64.b64decode(f.read()),encoding='utf8')
            info = [i.split(",") for i in dc.split("\n")]
    else:
        info = [            
            ('', '')
            ]          
    return info

lb_default = "请选择重连模式(点击可查看详细说明): "
lb_explain = """本工具仅供学习交流, 请勿用于商业等其他用途

1. 使用说明:    
    1.1 使用流程
        1.1.1 选择重连模式(非必选项)
        1.1.2 点击"开始运行"
        1.1.3 程序运行期间, 可保持较好的联网体验
        
    1.2 本工具依赖csust-bg连接互联网    
    1.3 当后台检测到掉线时, 会自动断网重连, 一般耗时 3-15s
    
2. 重连模式介绍:
    2.1. 常规模式: 比较稳定, 缺点是偶尔重连响应慢。
    2.2. 快速模式: 采取激进的断开wifi后重新连接的方案, 测试效果良好"""

def mouthOn(evt):
    box = messagebox.showinfo("使用须知",message=lb_explain)
    
def mouthHover(evt):
    lb_chooseMode.config(text=lb_default,fg="blue")

class netStatus(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("状态检测启动...")
        self.STAT = False
        
    def ping(self):
        COMMAND_PING = "ping www.baidu.com -n 1 -w 1000"        
        try:
            ans = subprocess.Popen(COMMAND_PING, stdin=-1, stdout=-1,stderr=-1,shell=True)
            ans.wait(1.5)
            self.STAT = ans.poll() == 0
        except:
            self.STAT = False
            
    def run(self):
        while True:
            self.ping()
            time.sleep(1)

def update_lb_status(api_stat):
    if api_stat:
        api_msg = "连接正常"
        api_color = "#008c00"
    else:
        api_msg = "连接异常, 正重试..."
        api_color = "yellow"
        
    msg = time.strftime("%H:%M:%S ") + MODE_DES[MODE] + " " + api_msg 
    lb_status.config(text=msg, bg=api_color)

def run():
    netstat = netStatus()
    netstat.setDaemon(True)
    
    utils = bg(3, "connLog.log", getInfo(), MODE==2)
    utils.setDaemon(True)
    
    netstat.start()
    utils.start()
    
    while True:
        if utils.STAT_CODE == 500:
            lb_status.config(text="错误: 当前不在可用范围,请检查后重试", bg="red")        
            return
        update_lb_status(netstat.STAT)
        time.sleep(1)

def start():
    lb_chooseMode.config(state=tkinter.DISABLED)
    lb_status.config(text="初始化中...")
    btn_start.config(text="正在运行中...",bg="white",state=tkinter.DISABLED)
    radio_button_normal.config(state=tkinter.DISABLED)
    radio_button_quick.config(state=tkinter.DISABLED)
    
    threading.Thread(target=run).start()
    
def modchange():
    global MODE
    res = v.get()
    MODE = res

## 配置窗口参数
tk = tkinter.Tk()
tk.title("csust-bg")

## 创建临时图标文件
with open("temp.ico",'wb') as templogo:
    templogo.write(base64.b64decode(logodata))
tk.iconbitmap("temp.ico")
os.remove("temp.ico")

wd_w = 240
wd_h = 160
scr_w = tk.winfo_screenwidth()/2
scr_h = tk.winfo_screenheight()/2
wd_size = f"{wd_w}x{wd_h}+{int(scr_w-0.5*wd_w)}+{int(scr_h-0.5*wd_h)}"
tk.geometry(wd_size)
tk.resizable(width=0, height=0)

## 构建 UI
lb_status = tkinter.Label(tk,text="连接状态",bg="#77787b",width=160)

lb_chooseMode = tkinter.Label(tk,text="请选择重连模式: ")
lb_chooseMode.bind("<Enter>",mouthHover)
lb_chooseMode.bind("<ButtonPress-1>",mouthOn)

v = tkinter.IntVar() # IntVar() 用于处理整数类型的变量
radio_button_normal = tkinter.Radiobutton(tk, text = '常规模式', variable = v,value =1,command=modchange)
radio_button_quick = tkinter.Radiobutton(tk, text = '快速模式', variable = v,value =2,command=modchange)
radio_button_normal.select()

btn_start = tkinter.Button(tk,text="点击开始",command=start,width=80,bg="#008c00",fg="white",border=0)

btn_start.pack(side="bottom")
lb_status.pack(side="top")
lb_chooseMode.pack(anchor ='w')
radio_button_normal.pack(anchor ='w')
radio_button_quick.pack(anchor ='w')

if __name__ == "__main__":
    ## 开始主循环
    tk.mainloop()
