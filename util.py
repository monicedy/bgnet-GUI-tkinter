import threading,random,requests,time,logging,os,sys,subprocess,base64

class bg(threading.Thread):
    def __init__(self, DEAMONTIME, logPath, info, reConnFlag):
        threading.Thread.__init__(self)
        self.reConnFlag = reConnFlag
        self.info = info
        self.DEAMONTIME = DEAMONTIME
        
        self.logPath = logPath
        logging.basicConfig(filename = self.logPath,level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.STAT_CODE = False
                
    def getAccts(self):
        return random.choice(self.info)

    def getParas(self):
        url = 'http://1.1.1.1/?isReback=1'
        para_s = time.time() ###
        try:
            paras = requests.get(url=url, allow_redirects=False, timeout=(3,3)).headers['Location'].split('&')
        except Exception as e:      
            return False, f"para err {e.__class__}"
        finally:
            self.mylog(f"para_duration: {time.time() - para_s}") ###
        
        wlanuserip,wlanacname,wlanacip,wlanusermac = [para.split('=')[-1] for para in paras]
        wlanusermac = '-'.join([ wlanusermac[i:i+2] for i in range(0,12,2) ])
        return True, 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Login&protocol=http:&hostname=192.168.7.221&iTermType=1&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&mac={wlanusermac}&ip={wlanuserip}&enAdvert=0&queryACIP=0&loginMethod=1'.format(wlanusermac=wlanusermac, wlanacip=wlanacip, wlanacname=wlanacname, wlanuserip=wlanuserip)

    def login(self):
        login_s = time.time()
        
        self.checkBg()
        # if self.ping():
        #     return True,''
        
        acct, pswd = self.getAccts()
        stat, parainfo = self.getParas()
        if not stat:
            return False, parainfo
        
        data = {'DDDDD': ',0,'+acct,    'upass': pswd,    'R1': '0',    'R2': '0',    'R3': '0',    'R6': '0',    'para': '00',    '0MKKey': '123456'}
        try:
            requests.post(url = parainfo, data = data)
            return True, (acct,pswd)
        except Exception as e:
            return False, f"post err {e.__class__}"
        finally:
            self.mylog(f"login_duration: {time.time()-login_s}")

    def ping(self):        
        COMMAND_PING = "ping www.baidu.com -n 1 -w 1000"        
        try:
            ans = subprocess.Popen(COMMAND_PING, stdin=-1, stdout=-1,stderr=-1,shell=True)
            ans.wait(1.5)
            res = ans.poll() == 0
            return res
        except:
            return False
        
        # COMMAND_PING = "ping www.baidu.com -n 1 -w 1000"        
        # try:
        #     ping_s = time.time() ###
        #     ans = subprocess.Popen(COMMAND_PING, stdin=-1, stdout=-1,stderr=-1,shell=True)
        #     ans.wait(1.5)
        #     res = ans.poll() == 0
        #     return res
        # except:
        #     return False
        # finally:            
        #     self.mylog(f"ping_duration: {time.time() - ping_s}")###
        
        # try:
        #     ping_s = time.time() ###
        #     ping_stat = 200 == requests.get('https://www.baidu.com',timeout=(1,1)).status_code
        #     return ping_stat
        # except:
        #     return False
        # finally:            
        #     self.mylog(f"ping_duration: {time.time() - ping_s}")###

    def mylog(self, msg):
        logging.info(msg)
        print(self.getTime() + msg)

    def getTime(self):
        return time.strftime("%m-%d %H:%M:%S ")
    
    def checkAvail(self):        
        COMMAND_CHECK_avail = 'netsh wlan show networks | find "csust-bg" '
        try:
            ans = subprocess.Popen(COMMAND_CHECK_avail, stdin=-1, stdout=-1,stderr=-1,shell=True)
            ans.wait(2)
            if ans.poll() == 0:
                return True
            else:
                self.mylog("csust-bg is not available")
                return False
        except Exception as e:
            self.mylog(f"check err: {e.__class__}")
            return False
    
    def checkBg(self):
        COMMAND_CHECK = 'netsh wlan show interface | find "csust-bg" '
        try:
            ans = subprocess.Popen(COMMAND_CHECK, stdin=-1, stdout=-1,stderr=-1,shell=True)
            ans.wait(1)
            if ans.poll() == 1:
                self.mylog("Not in csust-bg, Reconnect NOW!")
                self.reConn()
        except Exception as e:
            self.mylog(f"check err: {e.__class__}")
            return False
            
        # COMMAND_CHECK = "netsh wlan show interfaces"
        # try:
        #     info = os.popen(COMMAND_CHECK)
        #     if not "csust-bg" in info.read():
        #         self.mylog("Not in csust-bg, Reconnect NOW!")
        #         self.reConn()
        #     else:
        #         self.mylog("already in csust-bg")
        # except Exception as e:
        #     self.mylog(f"check err: {e.__class__}")
        #     return False

    def reConn(self):
        '''
            物理断网重连不要吝啬时间
        '''
        if not self.checkAvail():
            self.mylog("wifi is disable")
            self.STAT_CODE = 500 ## 内部错误  
            sys.exit(0)
            # assert self.checkAvail() 
            
        if self.ping():
            return True
        
        # reconn_s = time.time() ###
        # COMMAND_DISCONNECT = "netsh wlan disconnect"
        # COMMAND_RECONNECT = "netsh wlan connect name=csust-bg"
        # try:
        #     self.mylog('Disconnect...')
        #     statDisConn = subprocess.Popen(COMMAND_DISCONNECT, stdin=-1, stdout=-1,stderr=-1,shell=True)
        #     statDisConn.wait(4) # 14点54分：进一步优化重连耗时
        #     time.sleep(4) # 09点57分：5s通过（总耗时30s，测试3s
        #     # time.sleep(5)
        #     self.mylog('Reconnect to csust-bg...')
        #     statReConn = subprocess.Popen(COMMAND_RECONNECT, stdin=-1, stdout=-1,stderr=-1,shell=True)
        #     statReConn.wait(5) # 14点54分：进一步优化重连耗时
        #     time.sleep(5) 
        #     return statDisConn.poll() == 0 and statReConn.poll() ==0
        # except Exception as e:
        #     self.mylog(f"reConn err: {e.__class__}")
        #     return False
        # finally:
        #     self.mylog(f"reconn_duration: {time.time() - reconn_s}") ###
        
        COMMAND_DISCONNECT  = "netsh wlan disconnect"
        COMMAND_RECONNECT  = "netsh wlan connect name=csust-bg"
        try:
            self.mylog('Disconnect...')
            statDisConn = os.system(COMMAND_DISCONNECT)
            time.sleep(4)
            self.mylog('Reconnect to csust-bg...')
            statReConn = os.system(COMMAND_RECONNECT)
            time.sleep(5)        
            return statDisConn == 0 and statReConn ==0
        except Exception as e:
            self.mylog(f"reConn err: {e.__class__}")
            return False

    def deamon(self):
        while True:
            if not self.ping():                        
                self.STAT_CODE = False
                stat, msg = self.login()
                if not stat:
                    self.mylog(f"错误：{msg}")
                    if self.reConnFlag: #可选项
                        self.mylog(f"快速断网重连")
                        self.reConn()
                    time.sleep(1)
                else:
                    if not self.ping():
                        self.mylog("无效请求，将重试")
                        continue
                    
                    self.mylog("重连成功")
            else: 
                self.STAT_CODE = True
                # self.mylog("连接正常")
                time.sleep(self.DEAMONTIME)
        
    def run(self):
        self.mylog("Start!")
        if self.checkAvail():
            if not self.ping():
                self.checkBg()
            self.deamon()
        else:
            self.mylog("err: out of range!")
            self.STAT_CODE = 500 ## 内部错误
            return

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

def isReconn():
    flag = "quick" in sys.argv[0]
    if flag:
        print("快速模式")
        return True
    else:
        print("常规模式")
        return False
     
if __name__ == "__main__":
    notice='''
**************************************************************
- 使用说明: 后台每5s会检测一次网络状态, 并显示当前状态
- 注意事项: 鼠标不要点击终端, 如果上述状态不更新了, 可按回车继续
- 【可选】: 在文件名开头或末尾加"quick", 开启[快速重连]模式
        如: alwaysonlinequick.exe 或 quickalwayonline.exe
**************************************************************
    '''
    print(notice)
    
    freqSec = 5
    logPath = "connLog.log" 
    reConnFlag = isReconn()
    info = getInfo()
    
    csustbg = bg(freqSec, logPath, info, reConnFlag)
    # csustbg.setDaemon(True)
    csustbg.start()