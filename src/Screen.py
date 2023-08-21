from Event import Event
from Panel import Panel
from Utils import *

class Screen:
    def __init__(self, sda, screensect):
        self.sda = sda
        self.arrays = []        # for ScreenArray's
        self.panels = None      # set in configure
        self.pixels = {}        # screenpos -> [newbut, oldbut]
        self.keysdown = {}      # screenpos -> pressedbutton or None
        self.size = None
        self.configure(screensect)
        self.sda.scheduleEvent(2,RenderScreenEvent(self))

    def __str__(self):
        return self.__repr__()

    # def __repr__(self):
    #     return str(self.__class__.__module__) + "." + str(self.__class__.__name__) + "" + str(self.__dict__)

    def configure(self, ssect):
        self.size = ssect['size']
        ps = ssect['panels']
        if type(ps) not in [list,tuple]:
            ps = [ps]
        self.panels = ps
        self.renderHZ = ssect.get('renderHZ',10)
        print("screen.configure panels "+str(ps))

    def walkPixels(self,func):
        for idx, ary in self.pixels.items():
            func(self,idx,ary)

    def mapScreenPosKeyToButtonOrNone(self,spos,pressed):
        # Key releases need to be matched to the button
        # they originally pressed, even if the screen 
        # has changed out from underneath them since 
        print("MESSAGE:MAPSPK10",spos,pressed)
        if spos in self.keysdown:
            if not pressed:
                return self.keysdown.pop(spos)
            print("WARNING: IGNORED OVERLAPPING KEY PRESS AT",spos)
            return None
        print("MESSAGE:MAPSPK11",spos,pressed)
        if pressed:
            but = self.pixels.get(spos,[None])[0]
            print("MESSAGE:MAPSPKa11",spos,but,self.pixels)
            if but:
                self.keysdown[spos] = but
            return but
        print("WARNING: IGNORED UNMATCHED KEY RELEASE AT",spos)
        return None

    def renderPanels(self):
        #  1. Walk pixels and set names[1] = names[0] and names[0] = None
        def func(screen, idx, ary):
            ary[1] = ary[0]
            ary[0] = None
            #print("RP1: ",ary)
            return True
        self.walkPixels(func)
        
        #  2. Render panels to button names in names[0]
        def func(spos,panel,arg):
            #print("RENDER TO SCREEN YAH",spos,panel,arg)
            panel.renderButtons(self,spos,arg)
            return True
        Panel.walkPanels(func,{})
        #print("YAHOD",self.pixels)

        #  3. Walk pixels and update deck if names[0] !=
        #  names[1] or buttons[names[0]].isDirty()
        def func(screen, idx, ary):
            dirty = ary[0] != ary[1]
            if dirty or ary[0] is not None:
                screen.updateDeckAtPixel(idx,ary[0])
            return True
        self.walkPixels(func)

    def updateDeckAtPixel(self,idx,butornone):
        for sa in self.arrays:
            sa.updateScreenArrayAtScreenPixel(self,idx,butornone)

    def configureArrays(self,decks):
        for sdi in decks.streamdeckinfos:
            print("CONFIGURING",sdi)
            sa = ScreenArray(self,sdi.pos,sdi.size,sdi.deck,sdi)
            self.arrays.append(sa)

    #def getScreenArrayAtPt(self,pt):
    #    for sa in self.arrays:
            

    def placeButton(self,apos,butname):
        #print("placeButton",apos,butname)
        if apos not in self.pixels:
            self.pixels[apos] = [None, None]
        self.pixels[apos][0] = butname

class ScreenArray:    
    def __init__(self, screen, pos, size, deck, deckinfo):
        self.screen = screen
        self.pos = pos
        self.size = size
        self.deck = deck
        self.deckinfo = deckinfo

    def __str__(self):
        return self.__repr__()

    #def __repr__(self):
    #    return f"[{self.name}:{self.size[0]}x{self.size[1]}@{self.pos}]"

    def screenPosOfDeckPos(self,dpos):
        deckat = map2D(self.pos,self.size,dpos)
        if not deckat:
            return
        

    def updateScreenArrayAtScreenPixel(self,screen,pixel,butornone):
        deckat = map2D(self.pos,self.size,pixel)
        if not deckat:
            return
        deckidx = indexFrom2D(deckat,self.size)
        button = self.screen.sda.buttons.getButton(butornone)
        #print("UPDAP",self,pixel,butornone,button,deckat,deckidx)

        image = screen.sda.images.findButtonImage(button,self.deckinfo)
        #print("UPD2AP",deckidx,self.deck,image)
        self.deck.set_key_image(deckidx,image)
            

class RenderScreenEvent(Event):
    def __init__(self, screen):
        self.screen = screen

    def render(self):
        self.screen.renderPanels()

    def run(self,eq,now,dead):
        self.render()
        hz = self.screen.renderHZ
        eq.runIn(1/hz,self) #XXX .1,config

    
