from Utils import *

class Panel:
    screen = None
    panelmap = {}               # name -> panel
    toppanels = []              # panels with no parents

    @classmethod
    def getPanelOrNone(cls, panelname):
        return cls.panelmap.get(panelname,None)

    @classmethod
    def walkPanels(cls, func, arg):     # func(panel) returns falsey to stop walk
        cls.walkPanelsList((0,0),func,cls.toppanels,arg)

    @classmethod
    def walkPanelsList(cls, spos, func, kids, arg):
        for name in kids: 
            panel = cls.panelmap[name]
            if not panel.visible:
                continue
            newspos=add2D(spos,panel.pos)
            if not func(newspos, panel,arg):
                return False
            cls.walkPanelsList(newspos, func, panel.kids, arg)

    @classmethod
    def configurePanels(cls, screen, panelsect):
        cls.screen = screen
        def makePanel(name,attrs):
            print("MPATR "+name+ " " + str(attrs))
            if name not in cls.panelmap:
                panel = Panel(name, None)
                panel.kids = []
                panel.kidmap = {} # kidname -> kids index
                cls.panelmap[name] = panel

        for name, attrs in panelsect.items():
            makePanel(name,attrs)
        print("CFGPN: "+str(cls.panelmap))

        def linkPanel(name,attrs):
            print("LPATR "+name+" "+str(attrs))
            if 'parent' not in attrs:
                cls.toppanels.append(name)
            else:
                panel = cls.panelmap[name]
                par = attrs['parent']
                if par not in cls.panelmap:
                    assert(False,f"Unknown parent '{par}' in Panel '{name}")
                parent = cls.panelmap[par]
                if name not in parent.kidmap:
                    idx = len(parent.kids)
                    parent.kids.append(name)
                    parent.kidmap[name] = idx
                    panel.parent = par
                    print("ADKDKFN "+name+" to",parent.name,parent.kids)
                print("LINKED "+name+" to "+str(parent))

        for name, attrs in panelsect.items():
            linkPanel(name,attrs)

        print("CFGPN: "+str(cls.panelmap))
        print("TOP: "+str(cls.toppanels))

        toplevelsize = cls.screen.size
        for name in cls.toppanels: # default size and pos
            panel = cls.panelmap[name]
            if not hasattr(panel,'pos'):
                panel.pos = (0,0)
            if not hasattr(panel,'size'):
                panel.size = toplevelsize
            print("TLPCFG: "+str(panel))

        def packPanel(panel):
            print(f"packPanel {panel}")
            attrs = panelsect[panel.name]
            print(f"attrs {attrs}")
            parentname = None
            parent = None
            if hasattr(panel,'parent'):
                parentname = panel.parent
                parent = cls.panelmap.get(parentname,None)

            if 'size' not in attrs:
                panel.size = (1,1)
            elif attrs['size'] == 'fill':
                if not parent:
                    print(f"Cannot use 'size = fill' in unparented panel '{panel.name}'")
                    exit(2)
                panel.size = parent.size
                print("fill from parent "+str(panel)+" "+str(parent))
            else:
                panel.size = attrs['size']

            panel.type = attrs.get('type','normal')
            panel.pos = attrs.get('pos',(0,0))
            panel.visible = attrs.get('visible',True)
            panel.label = attrs.get('label',panel.name)

            # if 'pos' not in attrs:
            #     panel.pos = (0,0)
            # else:
            #     panel.pos = attrs['pos']

            if 'buttons' in attrs:
                panel.buttons = attrs['buttons']
                print("ZONGINBUT ",panel,panel.buttons)
                
            for kidname in panel.kids:
                kid = cls.panelmap[kidname]
                packPanel(kid)
                
        for name in cls.toppanels: # default size and pos
            panel = cls.panelmap[name]
            packPanel(panel)

        print("CFGPNLPK: "+str(cls.panelmap))

    def __init__(self, name, cfg):
        self.name = name
        self.label = name
        self.type = 'normal'    # or 'radio' or ..?
        self.pos = (0,0)
        self.size = (1,1)
        self.visible = False
        self.kids = []
        self.kidmap = {}
        self.buttons = []
        self.parent = None

    def __str__(self):
        return str(self.__class__.__module__) + "." + str(self.__class__.__name__) + "" + str(self.__dict__)

    def __repr__(self):
        return f"[{self.name}:{self.size[0]}x{self.size[1]}@{self.pos}]"

    def renderButtons(self, screen, spos, arg):
        #print("RNBUT",self,spos,arg,self.buttons)
        for y,row in enumerate(self.buttons):
            for x,but in enumerate(row):
                ppos = (x,y)
                apos = add2D(spos,ppos)
                screen.placeButton(apos,but)
        return True

    def popRadioKids(self):
        if self.type != 'radio':
            return
        for kn in self.kids:
            kid = self.panelmap[kn]
            kid.visible = False


    def setVisibility(self,show):
        parent = self.panelmap.get(self.parent,None)
        print("PNCSETVI",self,show,parent)
        if not show or not parent:
            self.visible = show
            return
        # Check if parent is radio
        print("PNCOPPS",self)
        parent.popRadioKids()
        self.visible = show
        print("PNCOOUT",self)
