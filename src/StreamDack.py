#!/usr/bin/env python3

import os
import shutil

import Event
import EventQueue
import Panel
import Screen
import Config
import Decks
import Image
import Button
import Action

class StreamDack:
    def __init__(self):
        self.EQ = EventQueue.EventQueue(self,"EQ")
        self.configPath = self.findConfigOrDie()
        self.loadConfig()
        sda = self.getRequiredSection('streamdack');
        self.bindirs = []       # paths in search order
        self.bindirmap = {}     # path->True
        if 'bindirs' in sda:
            for id in sda['bindirs']:
                self.addBinDir(id)
        if len(self.bindirs) == 0:
            self.addBinDir("")  # default path 

        self.screen = Screen.Screen(self,self.getRequiredSection('screen'))    # Check for required section early
        self.buttons = Button.Buttons(self,self.getRequiredSection('button'))
        self.images = Image.Images(self,sda)
        self.images.addImageDir(".")
        self.decks = Decks.Decks(self,self.getRequiredSection('deck'))      # Check for required section early
        self.actions = Action.Actions(self,self.getOptionalSection('action'))

        Panel.Panel.configurePanels(self,self.screen,self.getRequiredSection('panel')) # Check for required section early
        def reportPanel(spos,panel,arg):
            arg['count'] += 1
            print(str(arg['count']),spos,"WP:"+repr(panel))
            return True
        Panel.Panel.walkPanels(reportPanel,{'count' : 0})
        self.screen.configureArrays(self.decks)
        e = Event.Event.makeEvent(self,['action','setimage','layoutT2sday',"t2img/foo.png"])
        print("SLFKKLFD",e)

        # def demoButtonsVisitor(but,parents):
        #     print(f"{but}'s parents are {parents}")
        # Panel.Panel.visitButtons(demoButtonsVisitor)
        def setButtonParentVisitor(but,parents):
            but.addParent(parents[-1])
        Panel.Panel.visitButtons(setButtonParentVisitor)

    def addBinDir(self,path):
        epath = os.path.expanduser(path)
        if epath not in self.bindirmap:
            self.bindirs.append(epath)
            self.bindirmap[epath] = True

    def resolveProgram(self,prog):
        if prog[0] == '/':
            return prog
        for path in self.bindirs:
            aprog = os.path.join(path,prog)
            rprog = shutil.which(aprog)
            if rprog is not None:
                return rprog
        return None

    def findConfigOrDie(self):
        paths = []
        e = os.environ
        ekey ='STREAMDACKCONFIGPATH'
        if ekey in e:           # First try environmental variable
            paths.append(e[ekey])
        paths.append('~/.config/streamdack/streamdack.cfg') # Then 'std loc'
        paths.append('./streamdack.cfg')                    # Last ditch
        for p in paths:
            (exists,path) = self.expandPath(p)
            if exists:
                print(f"Found config file {path}")
                return path
        self.die(f"Config file not found in {paths}")

    def expandPath(self,path):
        epath = os.path.expanduser(path)
        if os.path.exists(epath):
            return (True,epath)
        return (False,None)

    def die(self,message):
        print(f"Error: {message}")
        exit(2)

    def getEventQueue(self):
        return self.EQ

    def getDeckBySerial(self,serial):
        info = self.decks.findDeckInfoIfAny(serial) # or None
        if info is not None:
            return info.deck
        return None

    def getDeckInfoBySerial(self,serial):
        return self.decks.findDeckInfoIfAny(serial) # or None

    def getRequiredSection(self,name):
        return self.config.getRequiredSection(name)

    def getOptionalSection(self,name):
        return self.config.getOptionalSection(name)

    def loadConfig(self):
        path = self.configPath
        if os.path.isfile(path):
            self.config = Config.Config("Cfg",path)
        else:
            self.die(f"Can't load {path}")
        self.config.load()
        self.config.print()


    def mainLoop(self):
        self.EQ.mainLoop()

    def scheduleEvent(self,time,event):
        self.EQ.runIn(time,event)

    def eqeg(self):
        print("hewo bongo")
        print(self.EQ)
        print("hewo bongo " + str(EQ))
        print("hewo bingo " + repr(EQ))

    def paneleg(self):
        p = Panel.Panel("zongK")
        print("sdsdkl "+repr(p))
        s = Screen.Screen("sdklskdlds")
        print("mahbookah "+repr(s))

    def configeg():
        c = Config.Config("Cfg","notes/foo.toml")
        print("sdsdkl "+repr(c))
        c.load()
        c.print()

    def run(self):
        self.mainLoop()
