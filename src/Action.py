from Utils import *
from Event import Event

class Actions:
    def __init__(self, sda, cfg):
        self.sda = sda          
        self.actionmap = {}       # actionname -> Action
        self.cfg = cfg
        self.maxdepth = cfg.get('maxdepth',5)
        print("ACTIONSINIT",cfg)

    def getAction(self,actionname):
        act = self.actionmap.get(actionname,None)
        if not act:
            #print("GETACTDDKD",actionname,self.cfg)
            cfg = self.cfg.get(actionname,{})
            act = Action(self,actionname,cfg)
            #print("GETACTD",act,cfg)
            self.actionmap[actionname] = act
        return act

    def __str__(self):
        return "AS:"+self.name

    def __repr__(self):
        return f"[{self.name}:{self.size[0]}x{self.size[1]}@{self.pos}]"

    def makeActionEvent(self,alist):
        #return Event.makeEvent(self.sda,['action',*alist])
        return Event.makeEvent(self.sda,alist)

class Action:
    def __init__(self, actions, name, cfg):
        self.actions = actions
        self.name = name
        #print("INITACT",cfg)
        self.acts = cfg.get('acts',None)
        if not self.acts:
            print(f"WARNING: No 'acts' found in {self.name}")
        #print("ACTMK",name,self.acts)

