import StreamDack
import sys

def exception_handler(exception_type, exception, traceback, debug_hook = sys.__excepthook__):
    print("EXCHNGZONGT",exception_type.__name__, exception)
    debug_hook(exception_type,exception,traceback)

def run():
    sys.excepthook = exception_handler
    print("HAROZONG")
    try:
        foo = bar
    except Exception as e:
        print("CLALDM",e)
    sd = StreamDack.StreamDack()
    sd.run()
    
