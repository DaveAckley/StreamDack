from abc import ABC, abstractmethod
import threading
import subprocess

from Panel import Panel

class Event(ABC):
    classmap = {}

    @classmethod
    def registerSubclass(cls,key,func):
        cls.classmap[key] = func

    @classmethod
    def makeEvent(cls,sda,list):
        try:
            action, type, *args = list
        except:
            print(f"'{list}' too short to be an action")
            return None
        if action != 'action':
            print(f"'{action}' is not 'action', in '{list}'")
            return None
        if type not in cls.classmap:
            print(f"'{type} is not a registered action type, in '{list}'")
            return None
        #print("EVMEV",type,args)
        return cls.classmap[type](sda,type,*args)

    def __init__(self,sda,name):
        self.sda = sda
        self.name = name
        self.sched = None

    def __str__(self):
        return str(self.__class__.__module__) + "." + str(self.__class__.__name__) + "" + str(self.__dict__)

    def __repr__(self):
        return "EVT:"+"DONG"

    @abstractmethod
    def run(self,eq,now,dead):
        pass

    
class DimScreenEvent(Event):
    def reschedule(self):
        delay = 60*60
        self.sda.scheduleEvent(delay,self) # one hour on
        
    def wake(self):
        self.reschedule();
        self.setBrightnessPercent(30)

    def run(self,eq,now,dead):
        self.setBrightnessPercent(0)
        delta = now - dead
        print(f'{dead} executed at {now} delay {delta}')

    def setBrightnessPercent(self,pct):
        decks = self.sda.decks
        decks.setAllDecksBrightness(pct);
        print(f'brightness now {pct}')

class ClockEvent(Event):

    def run(self,eq,now,dead):
        delta = now - dead
        print(f'{dead} executed at {now} delay {delta}')
        then = int(now/10)*10+10
        eq.runAt(then,self)

class SetImageEvent(Event):
    Event.registerSubclass('setimage',lambda sda,type,buttonname,imgpath: SetImageEvent(sda,type,buttonname,imgpath))

    def __init__(self,sda,name,button,image):
        super().__init__(sda,name)
        self.buttonname = button
        self.imagename = image
        
    def run(self,eq,now,dead):
        print("SETIM ",self,now)

class SetVisibleEvent(Event):
    Event.registerSubclass('show',lambda sda,type,panelname: SetVisibleEvent(sda,type,panelname))
    Event.registerSubclass('hide',lambda sda,type,panelname: SetVisibleEvent(sda,type,panelname))

    def __init__(self,sda,name,panel):
        super().__init__(sda,name)
        self.panelname = panel
        self.visibility = name == 'show'
        
    def run(self,eq,now,dead):
        panel = Panel.getPanelOrNone(self.panelname)
        if not panel:
            print(f"WARNING: Unknown panel '{self.panelname}' in {self}");
            return
        panel.setVisibility(self.visibility)
        
class ThreadEvent(Event):

    @abstractmethod
    def threadRun(self,eq,now,dead):
        pass

    def run(self,eq,now,dead):
        thread = threading.Thread(target=self.threadRun,args=(eq,now,dead))
        thread.start()


class SleepEvent(ThreadEvent):
    def threadRun(self,eq,now,dead):
        print("SLEEPEV "+str(now))
        eq.sleep(4)
        print("SLEEPEZ "+str(eq.now()))
        eq.runIn(3,self)
        
class ShellEvent(ThreadEvent):

    Event.registerSubclass('shell',lambda sda,type,*args: ShellEvent(sda,type,*args))

    def __init__(self,sda,name,*args):
        super().__init__(sda,name)
        #print(args)
        self.args = args
        
    def threadRun(self,eq,now,dead):
        cmd = self.args[0]
        cmda = cmd.split()
        prog = cmda[0]
        rprog = self.sda.resolveProgram(prog)
        if rprog is None:
            print(f"WARNING: NO EXECUTABLE '{prog}' FOUND; '{cmd}' IGNORED")
            return
        if rprog != prog:
            cmda[0] = rprog
            cmd = " ".join(cmda)

        print("SHELL",cmd)
        comp=subprocess.run(cmd,shell=True, capture_output=True)
        if comp.returncode != 0:
            print("WARNING:",comp.args,"exited",comp.returncode)
            print("STDOUT:",comp.stdout)
            print("STDERR:",comp.stderr)

class ButtonEvent(Event):
    #    Event.registerSubclass('button',lambda sda,type,panelname,vis: SetVisibleEvent(sda,type,panelname,vis))

    def __init__(self,sda,buttonname,state):
        super().__init__(sda,buttonname)
        self.sda = sda
        self.buttonname = buttonname
        self.newstate = state
        
    def run(self,eq,now,dead):
        buttons = self.sda.buttons
        #print("BUTKDNSAL",buttons)
        button = buttons.getButton(self.name)
        button.handleKeyEvent(self,eq,now,dead)

