import mouse, keyboard
import json
import time
from enum import IntEnum

def keyToScanCode(k: str) -> int:
    codes = []
    separator = {' ', '+', ','}
    exclude = {"right"}
    temp = ""
    length = len(k)
    for i in range(length):
        ch = k[i]
        if ch in separator:
            if temp:
                if temp in exclude and ch == " ":
                    temp += ch
                    continue
                codes.append(keyboard.key_to_scan_codes(temp)[0])
                temp = ""
            continue
        temp += ch
        
    if temp:
        codes.append(keyboard.key_to_scan_codes(temp)[0])
    
    if len(codes) == 1:
        return codes[0]
    return codes

class Hotkey:
    def __init__(self) -> None:
        self.__hotkey = set()
        self.__pressed = set()
        
    def setHotkey(self, h):
        if type(h) == str:
            h = keyToScanCode(h)
            for i in h:
                self.__hotkey.add(i)
        else:
            

class Recorder:
    class InputType(IntEnum):
        BUTTON = 0
        SCROLL = 1
        MOVE = 2
        KEY = 3
        
    class EventType(IntEnum):
        PRESS = 0
        RELEASE = 1
        
    class State(IntEnum):
        READY = 0
        RECORDING = 1
        PLAYING = 2
        
    def __init__(self) -> None:
        self.__record = []
        
    def __mouseInput(self, event):
        self.__record.append(event)
        
    def __keyboardInput(self, event):
        input = [self.InputType.KEY, event.name, event.scan_code]
        if event.event_type == "down":
            input.append(self.EventType.PRESS)
        else:
            input.append(self.EventType.RELEASE)
        input.append(event.is_keypad)
        input.append(event.time)
        self.__record.append(input)
        
    def __ready(self) -> set:
        print("[READY] Press hotkey to go")
        keyboard
        
    def record(self):
        # keyboard.hook()
        # mouse.hook(self.__mouseInput)
        keyboard.hook(self.__keyboardInput)
        
        keyboard.wait("ctrl + shift")
        
        # mouse.unhook_all()
        keyboard.unhook_all()
        
    def play(self):
        length = len(self.__record)
        i = 0
        
        
    def printRecord(self):
        for i in self.__record:
            print(i)
            
    def __mouseTest(self, event):
        print("====================")
        if type(event) == mouse.ButtonEvent:
            print("Type: {0}".format(type(event)))
            print("Button: {0}".format(event.button))
            print("Count: {0}".format(event.count))
            print("Event Type: {0}".format(event.event_type))
            print("Index: {0}".format(event.index))
            print("Time: {0}".format(event.time))
        elif type(event) == mouse.MoveEvent:
            print("Type: {0}".format(type(event)))
            print("Count: {0}".format(event.count))
            print("Index: {0}".format(event.index))
            print("Time: {0}".format(event.time))
            print("(x, y): ({0}, {1})".format(event.x, event.y))
        elif type(event) == mouse.WheelEvent:
            print("Type: {0}".format(type(event)))
            print("Count: {0}".format(event.count))
            print("Delta: {0}".format(event.delta))
            print("Index: {0}".format(event.index))
            print("Time: {0}".format(event.time))
        print("====================")
            
    def __keyboardTest(self, event):
        print("====================")
        print("Device: {0}".format(event.device))
        print("Event Type: {0}".format(event.event_type))
        print("Is Keypad: {0}".format(event.is_keypad))
        print("Modifiers: {0}".format(event.modifiers))
        print("Name: {0}".format(event.name))
        print("Scan Code: {0}".format(event.scan_code))
        print("Time: {0}".format(event.time))
        print("To json: {0}".format(event.to_json))
        print("====================")
        
    def test(self):
        mouse.hook(self.__mouseTest)
        keyboard.hook(self.__keyboardTest)
        
        keyboard.wait("ctrl + shift")
        
        mouse.unhook_all()
        keyboard.unhook_all()

def main():
    print(str(keyToScanCode("right shift + right ctrl")))
    input = Recorder()
    input.record()
    input.printRecord()
    # input.test()
    
if __name__ == "__main__":
    main()
    
# Notes
# use lists with IntEnum rather than dict in record

# keyboard
# [1] name
# [2] scan code
# [3] event type
# [4] is keypad
# [5] time