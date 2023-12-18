import mouse, keyboard
import json
import time
from enum import IntEnum
from pathlib import Path

class Hotkey:
    __pressed = set()
    __waiting = False
    
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
    
    def getHotkeyCode(self):
        return self.__hotkey_code
    
    def getHotkeyCombo(self):
        return self.__hotkey_combo
    
    @staticmethod
    def press(hotkey):
        hotkey = Hotkey.hotkeyToCode(hotkey, True)
            
        for i in hotkey:
            if i not in Hotkey.__pressed:
                keyboard.press(i)
                Hotkey.__pressed.add(i)
      
    @staticmethod          
    def release(hotkey):
        hotkey = Hotkey.hotkeyToCode(hotkey, True)
            
        for i in hotkey:
            if i in Hotkey.__pressed:
                keyboard.release(i)
                Hotkey.__pressed.remove(i)
                
    @staticmethod
    def tap(hotkey):
        hotkey = Hotkey.hotkeyToCode(hotkey, True)
        
        for i in hotkey:
            keyboard.press(i)
            keyboard.release(i)
                
    @staticmethod
    def wait(hotkeys):
        combos = {}
        if type(hotkeys) == list:
            for i in hotkeys:    
                combos[frozenset(Hotkey.hotkeyToCombo(i))] = i
        else:
            combos[frozenset(Hotkey.hotkeyToCombo(hotkeys))] = hotkeys
        
        Hotkey.__waiting = True
        k = ""
        while Hotkey.__waiting and frozenset(Hotkey.__pressed) not in combos.keys(): 
            k = keyboard.key_to_scan_codes(keyboard.read_key())[0]
            if k not in Hotkey.__pressed:
                Hotkey.__pressed.add(k)
            else:
                Hotkey.__pressed.remove(k)

        Hotkey.__waiting = False
        return combos[frozenset(Hotkey.__pressed)]
    
    @staticmethod
    def stopWait():
        Hotkey.__waiting = False
            
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
    def hotkeyToCode(keys, force_list=False) -> list:
        if type(keys) == Hotkey:
            keys = keys.getHotkeyCode()
            if not force_list and len(keys) == 1:
                return keys[0]
            return keys
        
        if type(keys) == str:
            keys = Hotkey.splitKeys(keys)
            
        if type(keys) == list:
            codes = []
            for i in keys:
                if type(i) == int:
                    codes.append(i)
                else:
                    codes.append(keyboard.key_to_scan_codes(i)[0])

            if not force_list and len(codes) == 1:
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
        RECORDING = 0
        PLAYING = 1
        
    class Hotkeys(IntEnum):
        START = 0
        PAUSE = 1
        STOP = 2
        CANCEL = 3
        
    def __init__(self, start_hotkey="ctrl + shift", pause_hotkey="", stop_hotkey="ctrl + alt", cancel_hotkey="ctrl + z") -> None:
        self.__record = []
        self.__pressed = set()
        self.__hotkeys = [Hotkey("ctrl+shift"), Hotkey(""), Hotkey("ctrl+alt"), Hotkey("ctrl+z")]
        self.__states = [False, False]
        
    def __start(self, state):
        if not self.__states[state]:
            self.__states[state] = True
            
    def __stop(self, state):
        if not self.__states[state]:
            self.__states[state] = False
        self.__hotkeys = [Hotkey(start_hotkey), Hotkey(pause_hotkey), Hotkey(stop_hotkey), Hotkey(cancel_hotkey)]
        
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
        
    def record(self):
        start_hotkey = self.__hotkeys[self.Hotkeys.START].getHotkeyName()
        cancel_hotkey = self.__hotkeys[self.Hotkeys.CANCEL].getHotkeyName()
        print("[READY] Press '{0}' to start recording or press '{1}' to cancel".format(start_hotkey, cancel_hotkey))
        
        keyboard.add_hotkey(start_hotkey, self.__start, args=[self.__states[self.State.RECORDING]])
        time.sleep(3)
        if self.__states[self.State.RECORDING]:
            print("recording")
        # start_hotkey = self.__hotkeys[self.Hotkeys.START].getHotkeyName()
        # cancel_hotkey = self.__hotkeys[self.Hotkeys.CANCEL].getHotkeyName()
        # print("[READY] Press '{0}' to start recording or press '{1}' to cancel".format(start_hotkey, cancel_hotkey))
        # choice = Hotkey.wait([start_hotkey, cancel_hotkey])
        
        # if choice == cancel_hotkey:
        #     print("[END] Recording cancelled")
        #     return

        # stop_hotkey = self.__hotkeys[self.Hotkeys.STOP].getHotkeyName()
        # print("[START] Recording input, press '{0}' to end record".format(stop_hotkey))
        
        # keyboard.hook(self.__keyboardInput)
        
        # Hotkey.wait(stop_hotkey)
        # print("[END] Recording stopped")
        
        # # mouse.unhook_all()
        # keyboard.unhook_all()
        
        
    def play(self):
        length = len(self.__record)
        i = 0
        
    def saveRecordToJson(self, record_name):
        data = json.dumps(self.__record)
        with open(record_name, 'w') as file:
            file.write(data)
        
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
    record_dir = Path(__file__).parent.parent.joinpath("records")
    input = Recorder()
    input.record()
    input.printRecord()
    input.saveRecordToJson(Path.joinpath(record_dir, "test.json"))
    
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