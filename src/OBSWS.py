import obsws_python as obsws
import logging
from Event import ThreadEvent

class OBSWS(ThreadEvent):
    def __init__(self, sda, name):
        print("OBSWS INITTING")
        #logging.basicConfig(level=logging.DEBUG) # See raw messages
        self.sda = sda
        self.name = name
        self.rcl = None
        self.ecl = None

    def threadRun(self,eq,now,dead):
        eq.runIn(2,self)
        self.checkConnections()

    def checkConnections(self):
        if self.rcl == None:
            self.tryReqConnect()
        if self.ecl == None:
            self.tryEvtConnect()

    def tryReqConnect(self):
        host = self.sda['wsaddress']
        port = self.sda['wsport']
        pswd = self.sda['wspassword']
        if host:
            try:
                self.rcl = obsws.ReqClient(host=host, port=port, password=pswd, timeout=3)
            except Exception as exc:
                print("OBSWS INIT (REQUEST) FAILED EXC",exc)
                self.rcl = None
                return

            #print("DIR",dir(self.rcl))
            resp = self.rcl.get_version()
            #print(resp.attrs())
            #print(resp.platform_description)
            #print(resp.obs_web_socket_version)
            #print(resp.available_requests)
            #print("ZONGIMGFMTS",resp.supported_image_formats)

            print(f"OBS Version: {resp.obs_version}")
            #rah = self.rcl.send("GetSceneList", raw=True)
            #print(rah)

        else:
            print("REQ NO HOST")

    def tryEvtConnect(self):
        host = self.sda['wsaddress']
        port = self.sda['wsport']
        pswd = self.sda['wspassword']
        if host:
            try:
                self.ecl = obsws.EventClient(host=host, port=port, password=pswd)
                print("ECL",self.ecl)
                def on_current_program_scene_changed(data):
                    print("OCPSC",data)
                    print("SCENE",data.scene_name)
                self.ecl.callback.register(on_current_program_scene_changed)
                print(self.ecl.callback.get())

            except Exception as exc:
                print("OBSWS INIT (EVENT) FAILED EXC",exc)
                self.ecl = None
                return

        else:
            print("EVT NO HOST")
        
    def sendReq(self,param,data=None):
        print("sendReq",param,data)
        try:
            resp = self.rcl.send(param,data)
        except obsws.error.OBSSDKRequestError as err:
            print("SENDREQ FAIL",err)
            self.rcl = None
            return None
            
        print("sendReqGOT",resp)
        return resp
    
            
