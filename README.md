# StreamDack

A one-week hack to scratch my own itch for controlling StreamDecks on Linux, from a single configuration file `streamdack.cfg`, with no GUI, no doc, and no support.

I had previously been using the excellent https://timothycrosley.github.io/streamdeck-ui , with my only complaint being an inability to trigger actions on StreamDeck key releases. Dealing with that complaint got a little out of hand and turned into this.

The StreamDack configuration file format is "TOML-ish" meaning it's TOML but unquoted strings that look like variable names are interpreted as strings. (Hmm I'll need to commit the `tomlikey` repo that supplies that too.)

StreamDack incorporates the great https://pypi.org/project/streamdeck/ library (on github at https://github.com/abcminiuser/python-elgato-streamdeck) to do all the H/W access. python-elgato-streamdeck is licensed under the MIT License.

StreamDack's design approach is to make a screen abstraction to represent all your StreamDecks, placed into a single 2D space like monitors in a multi-monitor setup. But instead of being a screen of pixels it is a screen of StreamDeck keys. A hierarchical `panel` window manager redraws that screen, ultimately associating each key with a configurable `Button`, which can trigger `Action` sequences on key press or release or both. Action types include shell commands and changing visibility of Panels.
