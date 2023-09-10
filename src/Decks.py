import os
# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

import asyncio
import time

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

from Utils import *
from Screen import ScreenArray
from Event import ButtonEvent
import Button

class DeckInfo:
    def __init__(self,name,cfg):
        self.name = name
        self.serial = cfg['serial']
        self.pos = cfg['pos']
        if 'size' in cfg:
            self.size = cfg['size']

    def __str__(self):
        return "DI:"+self.name+"/"+self.serial

    def __repr__(self):
        return str(self)

    def addDeck(self, index, deck, decks):
        self.decks = decks
        self.deck = deck
        self.number = index
        self.type = deck.DECK_TYPE
        self.firmware = deck.get_firmware_version()
        self.serial = deck.get_serial_number()
        self.isvisual = deck.is_visual()
        if self.isvisual:
            self.imageformat = deck.key_image_format()
            self.imageformatstr = str(self.imageformat)
        dsize = (deck.KEY_COLS, deck.KEY_ROWS)
        if hasattr(self,'size'):
            if dsize[0] != self.size[0] or dsize[1] != self.size[1]:
                print(f"Deck '{self.name}': Overriding configured size {self.size} with {dsize}")
        self.size = dsize

class Decks:
    def __init__(self,streamdack,decsect):
        self.sda = streamdack
        self.streamdeckinfos = []
        self.deckmap = {}      # serial -> deckinfo 
        self.configure(decsect)
        self.initDecks()

    def configure(self,decsect):
        for name, decki in decsect.items():
            print(f"Decks.configure {name} {decki}")
            deckinfo = DeckInfo(name,decki)
            self.streamdeckinfos.append(deckinfo)
            self.deckmap[deckinfo.serial] = deckinfo

    def findDeckInfoIfAny(self,serial):
        if serial in self.deckmap:
            return self.deckmap[serial]
        return None

    def setAllDecksBrightness(self,percent):
        for index, deck in enumerate(self.streamdecks):
            if not deck.is_visual():
                continue
            #print(f'{deck} brightness {percent}')
            deck.set_brightness(percent)
        
    def initDecks(self):
        self.streamdecks = DeviceManager().enumerate()
        print("Found {} Stream Deck(s).\n".format(len(self.streamdecks)))
        print("viz {}\n".format(self.streamdecks))

        for index, deck in enumerate(self.streamdecks):
            # This example only works with devices that have screens.
            #if not deck.is_visual():
            #   continue

            print("TRYING TO OPEN DEVICE {} {}".format(index,deck))
            deck.open()
            print("TRYING TO RESET DEVICE {}".format(index))
            deck.reset()

            serial = deck.get_serial_number()
            deck.originalSerial = serial # ADD originalSerial data member

            print("Device {} serial number: '{}'".format(index,serial))

            info = self.findDeckInfoIfAny(serial)
            if info is None:
                print("No configuration found for device '{}', ignoring".format(serial))
                deck.close()
                continue

            info.addDeck(index,deck,self)
            
            print("Configured deck '{}' (type: '{}' serial number: '{}', fw: '{}')".format(
                info.name, info.type, info.serial, info.firmware
            ))

            # Set initial key images.
            nullButton = Button.Button(self.sda.buttons,"",{'image' : 'black.png'})
            nullButtonImage = self.sda.images.findButtonImage(nullButton,info)

            for key in range(deck.key_count()):
                deck.set_key_image(key, nullButtonImage)

                # Register callback function for when a key state changes.
                deck.set_key_callback(lambda deck, key, state : self.key_change_callback(deck,key,state))

            # SKIP REST IF NO SCREEN
            if not deck.is_visual():
                continue

            # Set initial screen brightness to 30%.
            deck.set_brightness(30)

            # Wait until all application threads have terminated (for this example,
            # this is when all deck handles are closed).
            # for t in threading.enumerate():
            #     try:
            #         t.join()
            #     except RuntimeError:
            #         pass


            #    def deck_and_key_to_pos(self, deck, keynum):
            #        print("deck_and_key_to_pos{deck.KEY_COLS}x{deck.KEY_ROWS}");

    # Generates a custom tile with run-time generated text and custom image via the
    # PIL module.
    def render_key_image_for_button(self, deck, icon_filename, font_filename, font_fg, font_bg, font_size, label_text, label_pos):
        # Resize the source image asset to best-fit the dimensions of a single key,
        # leaving a margin at the bottom so that we can draw the key title
        # afterwards.
        icon = Image.open(icon_filename)
        image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 0, 0])

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image a few pixels from the bottom of the key.
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_filename, font_size)
        pixUp = label_pos[1]+font_size-2
        pixOver = label_pos[0]
        for x in range(-1,2):
            for y in range(-1,2):
                if x==0 and y==0:
                    continue
                draw.text((image.width / 2 - x - pixOver, image.height - pixUp - y),
                          text=label_text, font=font, anchor="ms", fill=font_bg)
        draw.text((image.width / 2 - pixOver - 0, image.height - pixUp - 0),
                  text=label_text, font=font, anchor="ms", fill=font_fg)

        return PILHelper.to_native_format(deck, image)

    # Returns styling information for a key based on its position and state.
    def get_key_style(self, deck, key, state):
        # Last button in the example application is the exit button.
        exit_key_index = deck.key_count() - 1

        if key == exit_key_index:
            name = "exit"
            icon = "{}.png".format("Exit")
            font = "Roboto-Regular.ttf"
            label = "Bye" if state else "Exit"
        else:
            name = "emoji"
            icon = "{}.png".format("Pressed11" if state else "Released")
            font = "Roboto-Regular.ttf"
            label = "Pressed!" if state else "Key {}".format(key)

        return {
            "name": name,
            "icon": os.path.join(ASSETS_PATH, icon),
            "font": os.path.join(ASSETS_PATH, font),
            "label": label
        }

    # Creates a new key image based on given impath path and text
    # label, using a default style
    def make_key_image(self, deck, path, label):
        # Determine what icon and label to use on the generated key.
        key_style = self.get_key_style(deck, label, False)

        # Generate the custom key with the requested image and label.
        image = self.render_key_image(deck, path, key_style["font"], label)
        return image

    # Creates a new key image based on given button config
    def make_key_image_for_button(self, fullpath, deck, button):
        label_text = button.label or "-"
        label_pos = button.labelpos
        label_anchor = button.labelanchor
        font_filename = button.font
        font_fg = button.fontfg
        font_bg = button.fontbg
        font_size = button.fontsize
        margins = button.margins
        edgecrop = button.crop

        icon = Image.open(fullpath)
        crops = (edgecrop[0],edgecrop[1],
                 icon.width-edgecrop[2],
                 icon.height-edgecrop[3])
        icon = icon.crop(crops)
        
        image = PILHelper.create_scaled_image(deck, icon, margins=margins)

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image a few pixels from the bottom of the key.
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_filename, font_size)
        pixUp = (1.0 - label_pos[1])*image.height
        pixOver = label_pos[0]*image.width
        #print("FONGFG",font_fg,label_text,button)
        if font_bg != "None":
            for x in range(-1,2):
                for y in range(-1,2):
                    if x==0 and y==0:
                        continue
                    draw.text((pixOver - x, pixUp - y),
                              text=label_text, font=font, anchor=label_anchor, fill=font_bg)
        if font_fg != "None":
            draw.text((pixOver, pixUp),
                      text=label_text, font=font, anchor=label_anchor, fill=font_fg)

        return PILHelper.to_native_format(deck, image)

        # Generate the custom key with the requested image and label.
        image = self.render_key_image(deck, fullpath, font, fontfg, fontbg, fontsz, label, labelpos)
        return image

    # Creates a new key image based on the key index, style and current key state
    # and updates the image on the StreamDeck.
    def update_key_image(self, deck, key, state):
        # Determine what icon and label to use on the generated key.
        key_style = self.get_key_style(deck, key, state)

        # Generate the custom key with the requested image and label.
        image = self.render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

        # Use a scoped-with on the deck to ensure we're the only thread using it
        # right now.
        with deck:
            # Update requested key with the generated image.
            deck.set_key_image(key, image)

    # Prints key state change information, updates rhe key image and performs any
    # associated actions when a key is pressed.
    def key_change_callback(self, deck, key, state):
        info = self.deckmap[deck.originalSerial]
        screen = self.sda.screen
        dpos = indexTo2D(key,info.size)
        spos = add2D(dpos,info.pos)
        butnone = screen.mapScreenPosKeyToButtonOrNone(spos,state)
        if butnone:
            event = ButtonEvent(self.sda,butnone,state)
            self.sda.scheduleEvent(0,event)

    # def dookeychange(self, deck, key, state):

    #     # Print new key state
    #     print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    #     # Update the key image based on the new key state.
    #     update_key_image(deck, key, state)

    #     # Check if the key is changing to the pressed state.
    #     if state:
    #         key_style = get_key_style(deck, key, state)

    #     # When an exit button is pressed, close the application.
    #     if key_style["name"] == "exit":
    #         # Use a scoped-with on the deck to ensure we're the only thread
    #         # using it right now.
    #         with deck:
    #             # Reset deck, clearing all button images.
    #             deck.reset()

    #             # Close deck handle, terminating internal worker threads.
    #             deck.close()
