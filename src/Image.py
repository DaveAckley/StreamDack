import os

import Button

class Images:
    def __init__(self,streamdack,opts):
        self.sda = streamdack
        self.imagedirs = []     # paths in search order
        self.imagedirmap = {}   # path->True
        self.imagecache = {}    # (imageformatstr,path)->(fullpath,Image)
        if 'imagedirs' in opts:
            for id in opts['imagedirs']:
                self.addImageDir(id)
        self.addImageDir(os.path.join(os.path.dirname(__file__), "Assets"))
        print(self)

    def __str__(self):
        return str(self.__class__.__name__) + "" + str(self.__dict__)
        
    def addImageDir(self,path):
        epath = os.path.expanduser(path)
        if epath not in self.imagedirmap:
            self.imagedirs.append(epath)
            self.imagedirmap[epath] = True

    # def findImagePath(self,path):
    #     if path[0] == '/':
    #         return path
    #     for id in self.imagedirs:
    #         full = os.path.join(id,path)
    #         if os.path.isfile(full):
    #             return full
    #     return None

    def walkImagePaths(self,path,func):
        if path[0] == '/':
            return func(path)
        for id in self.imagedirs:
            full = os.path.join(id,path)
            if os.path.isfile(full):
                ret = func(full)
                if ret:
                    return ret
        return None
        
    def findButtonImage(self,button,deckinfo):
        path = button.image
        #print("FINBUDINKMG",path)
        for id in self.imagedirs:
            full = os.path.join(id,path)
            #print("FINDUBITER",full)
            if os.path.isfile(full):
                image = self.getButtonImage(full,button,deckinfo)
                if image:
                    #print("FINUDITERGOT",full,image)
                    return image
        return None

    # def findImage(self,path,deckinfo):
    #     #print("FINDINKMG",path)
    #     for id in self.imagedirs:
    #         full = os.path.join(id,path)
    #         #print("FINDITER",full)
    #         if os.path.isfile(full):
    #             image = self.getImage(full,deckinfo)
    #             if image:
    #                 #print("FINDITERGOT",full,image)
    #                 return image
    #     return None
            
    def getButtonImage(self,fullpath,button,deckinfo):
        key = (str(button), fullpath, deckinfo.imageformatstr)
        #print("IMGIMK",key,fullpath)
        if key in self.imagecache:
            (full,image) = self.imagecache[key]
            #print("getIMGICACH",image)
            return image
        image = self.renderButtonImage(fullpath,button,deckinfo)
        self.imagecache[key] = (fullpath,image)
        print("GETIMGINEW",key,image)
        return image

    # def getImage(self,path,deckinfo):
    #     key = (deckinfo.imageformatstr, path)
    #     #print("IMGIMK",key,path)
    #     if key in self.imagecache:
    #         (full,image) = self.imagecache[key]
    #         #print("getIMGICACH",image)
    #         return image
    #     image = self.renderImage(path,deckinfo)
    #     self.imagecache[key] = (path,image)
    #     #print("GETIMGINEW",image)
    #     return image

    def renderButtonImage(self,fullpath,button,deckinfo):
        decks = deckinfo.decks
        deck = deckinfo.deck
        image = decks.make_key_image_for_button(fullpath,deck,button)
        print("RNDIMPS",fullpath,deckinfo.serial,image)
        return image

    # def renderImage(self,path,deckinfo):
    #     decks = deckinfo.decks
    #     deck = deckinfo.deck
    #     image = decks.make_key_image(deck,path,"FOOE")
    #     print("RNDIMPS",path,deckinfo.serial,image)
    #     return image

class Image:
    def __init__(self,path):
        self.path=path
        
