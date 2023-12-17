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
    __pressed = set()
    
    def __init__(self, hotkey="") -> None:
        self.__hotkey = []
        self.__hotkey_code = []
        self.__hotkey_combo = set()
        self.setHotkey(hotkey)
        
    def setHotkey(self, hotkey):
        if type(hotkey) == str:
            self.__hotkey = Hotkey.splitKeys(hotkey)
        elif type(hotkey) == list:
            self.__hotkey = hotkey
            
        self.__hotkey_code = Hotkey.hotkeyToCode(self.__hotkey)
        if type(self.__hotkey_code) == int:
            self.__hotkey_code = [self.__hotkey_code]
            
        self.__hotkey_combo = Hotkey.hotkeyToCombo(self.__hotkey_code)
    
    def getHotkey(self):
        return self.__hotkey
    
    def getHotkeyName(self):
        hotkey = ""
        length = len(self.__hotkey)
        for i in range(length):
            key = self.__hotkey[i]
            hotkey += key
            if i < length-1:
                hotkey += " + "
        
        return hotkey
    
    def getHotkeyCombo(self):
        return self.__hotkey[1]
    
    def press(self):
        for i in self.__hotkey_code:
            if i not in Hotkey.__pressed:
                keyboard.press(i)
                Hotkey.__pressed.add(i)
                
    def release(self):
        for i in self.__hotkey_code:
            if i in Hotkey.__pressed:
                keyboard.release(i)
                Hotkey.__pressed.remove(i)
            
    @staticmethod
    def splitKeys(k: str) -> list:
        exclude = {'+', ' '}
        direction = {"right"}
        key = ""
        keys = []
        for i in range(len(k)):
            ch = k[i]
            if ch not in exclude:
                if key in direction:
                    key += ' '
                key += ch
                continue
            
            if ch == ' ':
                continue
            
            if ch == '+' and key:
                keys.append(key)
                key = ""
                
        if key:
            keys.append(key)
        
        return keys
    
    @staticmethod
    def hotkeyToCode(keys) -> list:
        if type(keys) == str:
            keys = Hotkey.splitKeys(keys)
            
        if type(keys) == list:
            codes = []
            for i in keys:
                if type(i) == int:
                    codes.append(i)
                else:
                    codes.append(keyboard.key_to_scan_codes(i)[0])

            if len(codes) == 1:
                return codes[0]
            return codes
        
    @staticmethod
    def hotkeyToCombo(keys) -> set:
        if type(keys) == str:
            keys = Hotkey.splitKeys(keys)
            
        if type(keys) == list:
            combo = set()
            for i in keys:
                if type(i) == str:
                    combo.add(keyboard.key_to_scan_codes(i)[0])
                elif type(i) == int:
                    combo.add(i)
            
            return combo

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
        
    class Hotkeys(IntEnum):
        START = 0
        PAUSE = 1
        STOP = 2
        CANCEL = 3
        
    def __init__(self) -> None:
        self.__record = []
        self.__pressed = set()
        self.__hotkeys = [Hotkey("ctrl+shift"), Hotkey(""), Hotkey("ctrl+alt"), Hotkey("ctrl+z")]
        
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
        
    def ready(self, message) -> set:
        print("[READY] " + message)
        start = self.__hotkeys[self.Hotkeys.START].getHotkeyCombo()
        cancel = self.__hotkeys[self.Hotkeys.CANCEL].getHotkeyCombo()
        k = ""
        while self.__pressed != start and self.__pressed != cancel:
            k = keyboard.key_to_scan_codes(keyboard.read_key())[0]
            self.__evaluatePress(k)

        hotkey_used = -1
        if self.__pressed == start:
            hotkey_used = self.Hotkeys.START
        else:
            hotkey_used = self.Hotkeys.CANCEL
        self.__pressed.clear()
        
        return hotkey_used
        
    def record(self):
        # keyboard.hook()
        # mouse.hook(self.__mouseInput)
        start_hotkey = self.__hotkeys[self.Hotkeys.START].getHotkeyName()
        cancel_hotkey = self.__hotkeys[self.Hotkeys.CANCEL].getHotkeyName()
        choice = self.ready(message="Press '{0}' to start recording, press '{1}' to cancel".format(start_hotkey, cancel_hotkey))
        
        if choice == self.Hotkeys.CANCEL:
            print("[END] Recording cancelled")
            return

        print("[START] Recording input, press '{0}' to end record".format(self.__hotkeys[self.Hotkeys.STOP].getHotkeyName()))
        
        keyboard.hook(self.__keyboardInput)
        
        keyboard.wait("ctrl + alt")
        
        # mouse.unhook_all()
        keyboard.unhook_all()
        
    def play(self):
        length = len(self.__record)
        i = 0
        
    def __evaluatePress(self, k):
        if k not in self.__pressed:
            self.__pressed.add(k)
        else:
            self.__pressed.remove(k)
        
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
    # input = Recorder()
    # input.record()
    hotkey = Hotkey("q+p+7+8")
    time.sleep(2)
    hotkey.press()
    time.sleep(3)
    hotkey.release()
    
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