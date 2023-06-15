#!/usr/bin/env python3

import os

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
        self.screen = Screen.Screen(self,self.getRequiredSection('screen'))    # Check for required section early
        self.buttons = Button.Buttons(self,self.getRequiredSection('button'))
        self.images = Image.Images(self,self.getRequiredSection('streamdack'))
        self.images.addImageDir(".")
        self.decks = Decks.Decks(self,self.getRequiredSection('deck'))      # Check for required section early
        self.actions = Action.Actions(self,self.getOptionalSection('action'))

        Panel.Panel.configurePanels(self.screen,self.getRequiredSection('panel')) # Check for required section early
        def reportPanel(spos,panel,arg):
            arg['count'] += 1
            print(str(arg['count']),spos,"WP:"+repr(panel))
            return True
        Panel.Panel.walkPanels(reportPanel,{'count' : 0})
        self.screen.configureArrays(self.decks)
        e = Event.Event.makeEvent(self,['action','setimage','layoutT2sday',"t2img/foo.png"])
        print("SLFKKLFD",e)

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
