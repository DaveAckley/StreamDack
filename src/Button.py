from Utils import *
from Event import Event

class Buttons:
    def __init__(self, sda, cfg):
        self.sda = sda          
        self.buttonmap = {}              # name -> Button
        self.cfg = cfg
        #print("BUTTONSCFDGF",cfg)

    def getButton(self,buttonname):
        but = self.buttonmap.get(buttonname,None)
        if not but:
            cfg = self.cfg.get(buttonname,{})
            but = Button(self,buttonname,cfg)
            #print("GETBUMD",but,cfg)
            self.buttonmap[buttonname] = but
        #print("GETBURET",but)
        return but
        
class Button:
    def __init__(self, buttons, name, cfg):
        self.buttons = buttons
        self.name = name
        self.font = cfg.get('font',"Roboto-Regular.ttf")
        self.fontsize = cfg.get('fontsize',14)
        self.fontfg = cfg.get('fontfg',"white")
        self.fontbg = cfg.get('fontbg',"black")

        self.label = cfg.get('label',name)
        self.labelpos = cfg.get('labelpos',(0.5,0.1))
        self.labelanchor = cfg.get('labelanchor',"ms")
        
        self.image = cfg.get('image',"black.png")
        self.crop = cfg.get('crop',[0,0,0,0])
        self.margins = cfg.get('margins',[0,0,0,0])
        self.onpress = cfg.get('press',[])       # list of Action 
        #print("BUTIN",name,cfg,self.onpress)
        self.onrelease = cfg.get('release',[])   # list of Action 

        self.sustainer = cfg.get('sustainer',False)        # set True for sustain buttons, or WTFK
        
        self.count = 0          # ++ on press, -- on release
        self.parentMap = {}     # panelName->panel that mention this Button
        self.parentList = []    # panelNames that contain this Button in visitation order

    def addParent(self,parent):
        pname = parent.name
        if pname not in self.parentMap:
            self.parentMap[pname] = parent
            self.parentList.append(pname)
            print(f"But {self.name} parents now {self.parentList}")

    def __str__(self):
        return (f'BTN({self.label},{self.labelpos},{self.labelanchor},'
                f'{self.font},{self.fontsize},{self.fontfg},{self.fontbg},'
                f'{self.crop},{self.margins})')

    def __repr__(self):
        return f"[{self.name}:{self.size[0]}x{self.size[1]}@{self.pos}]"

    def render(self, screen, spos, arg):
        #print("RNDBUT",self,spos,arg)
        return True

    def runActions(self,actionlist):
        return self.runActionsHelper(actionlist,0)

    def failActions(self,actionlist,depth):
        print(f"WARNING: Depth {depth}: {actionlist}")
        return False
    
    def runActionsHelper(self,actionlist,depth):
        sda = self.buttons.sda
        actions = sda.actions
        maxdepth = actions.maxdepth
        if depth > maxdepth:
            print(f"WARNING: Action.maxdepth={maxdepth} exceeded, abandoning action");
            return self.failActions(actionlist,depth)
        eq = sda.EQ
        #print("RUNACTIONS",self.name,actionlist)
        if isinstance(actionlist,list):   # inline action or list of actions
            if len(actionlist) > 0:
                if actionlist[0] == 'action': # inline action
                    event = sda.actions.makeActionEvent(actionlist)
                    #print("RUNACTIONS3",event)
                    eq.runIn(0,event)
                else:
                    for alist in actionlist: # list of actions
                        if not self.runActionsHelper(alist,depth+1):
                            return self.failActions(actionlist,depth)
        elif actionlist is not None: # single named action
            action = sda.actions.getAction(actionlist)
            #print("RUNACTION0",action.acts)
            if not self.runActionsHelper(action.acts,depth+1):
                return self.failActions(actionlist,depth)
        return True

    def sustainOrRelease(self):
        visitedPanels = {}
        for pname in self.parentList:
            panel = self.parentMap[pname]
            if panel.sustainsButton(self,visitedPanels):
                return          # someone took it
        #print(f"SORB releasing {self.name}")
        self.runActions(self.onrelease) # noone took it


    def handleKeyEvent(self,buttonevent,eq,now,dead):
        sda = self.buttons.sda
        sda.EQ.dimmer.wake()

        press = buttonevent.newstate
        #print("BUTTONEVENTEC",self.name,press,self.count,now)
        if press:
            self.count = self.count+1
            if self.count == 1:
                #print(f"HKE pressing {self.name}")
                self.runActions(self.onpress)
        else:
            self.count = self.count-1
            if self.count == 0:
                if self.sustainer: # don't try to sustain sustainers
                    #print(f"HKE release sustainer {self.name}")
                    self.runActions(self.onrelease)
                else:
                    #print(f"HKE sustain OR RELEASEO {self.name}")
                    self.sustainOrRelease()

        return True
