import time as __time
import logging as __logging
import json as __json
import argparse as __argparse
from enum import IntEnum as __IntEnum
from pathlib import Path as __path
from pynput import mouse as __mouse
from pynput import keyboard as __keyboard
from bidict import bidict as __bidict

__logging.basicConfig(format="[%(levelname)s] %(message)s")
__log = __logging.getLogger()
__log.setLevel(__logging.INFO)

__pressed = set()
__keys = __bidict({'""': 222, '*': 106, '+': 107, ',': 188, '-': 109, '.': 190, '/': 191, '0': 48, '1': 49, '2': 50, '3': 51, '4': 52, 
    '5': 53, '6': 54, '7': 55, '8': 56, '9': 57, ';': 186, '<100>': 100, '<101>': 101, '<102>': 102, '<103>': 103, 
    '<104>': 104, '<105>': 105, '<110>': 110, '<96>': 96, '<97>': 97, '<98>': 98, '<99>': 99, '=': 187, "alt_r": 165,
    "alt": 164, "backspace": 8, "caps_lock": 20, "cmd": 91, "ctrl": 162, "ctrl_r": 163, 
    "delete": 46, "down": 40, "enter": 13, "esc": 27, "f1": 112, "f10": 121, "f11": 122, 
    "f12": 123, "f2": 113, "f3": 114, "f4": 115, "f5": 116, "f6": 117, "f7": 118, "f8": 119, 
    "f9": 120, "insert": 45, "left": 37, "media_next": 176, "media_play_pause": 179, 
    "media_previous": 177, "media_volume_down": 174, "media_volume_mute": 173, "media_volume_up": 175, 
    "num_lock": 144, "print_screen": 44, "right": 39, "shift": 160, "shift_r": 161, "space": 32, 
    "tab": 9, "up": 38, '[': 219, '\\\\': 220, ']': 221, '`': 192, 'a': 65, 'b': 66, 'c': 67, 'd': 68, 'e': 69, 
    'f': 70, 'g': 71, 'h': 72, 'i': 73, 'j': 74, 'k': 75, 'l': 76, 'm': 77, 'n': 78, 'o': 79, 'p': 80, 'q': 81, 'r': 82, 
    's': 83, 't': 84, 'u': 85, 'v': 86, 'w': 87, 'x': 88, 'y': 89, 'z': 90})
__buttons = __bidict({"LMB": __mouse.Button.left, "MMD": __mouse.Button.middle, "RMB": __mouse.Button.right, 
                      "X1": __mouse.Button.x1, "X2": __mouse.Button.x2})

def typeVal(v):
    print("{0} | {1}".format(type(v), v))

# def press(key):
#     if type(key) == str:
#         key = Hotkey.parse(key)
#     elif type(key) == Hotkey:
#         key = key.getHotkeyCode()
        
#     kb = __keyboard.Controller()
#     for i in key:
#         kb.press(i)
        
# def release(key):
#     if type(key) == str:
#         key = Hotkey.parse(key)
    
#     kb = __keyboard.Controller()
#     for i in key:
#         kb.release(i)

class Hotkey:
    
    
    def __init__(self, hotkey="") -> None:
        self.__hotkey = []
        self.__hotkey_combo = set()
        self.setHotkey(hotkey)
        
    def getHotkey(self):
        return self.__hotkey
        
    def getHotkeyName(self):
        name = ""
        length = len(self.__hotkey)
        for i in range(length):
            key = self.__hotkey[i]
            name += key
            if i < length-1:
                name += " + "
        return name
    
    def getHotkeyCombo(self):
        return self.__hotkey_combo
    
    def setHotkey(self, hotkey):
        if type(hotkey) == str:
            self.__hotkey = Hotkey.parse(hotkey)
        elif type(hotkey) == list:
            for i in hotkey:
                if type(i) == str:
                    self.__hotkey.append(i)
        
        self.__hotkey_combo = Hotkey.keyToCombo(self.__hotkey)
        
    def setHotkeyFromInput(self):
        self.__hotkey.clear()
        self.__hotkey_combo.clear()
        with __keyboard.Listener(on_press=self.__onPress, on_release=self.__onRelease) as listener:    
            listener.join()
        
    def __onPress(self, key):
        key_code = Hotkey.hotkeyToCode(key)
        if key_code not in Hotkey.__pressed:
            if __keyboard.Key.ctrl_l.value.vk in Hotkey.__pressed:
                print("ctrl pressed")
                __keyboard.Controller().release(__keyboard.Key.ctrl_l)
            Hotkey.__pressed.add(key_code)
            self.__hotkey.append(key)
            self.__hotkey_combo.add(key_code)
            
    def __onRelease(self, key):
        if key == __keyboard.Key.ctrl_l:
            return
        Hotkey.__pressed.clear()
        return False
    
    @staticmethod
    def getPressedKeys():
        return Hotkey.__pressed
    
    @staticmethod
    def addToPressedKeys(key):
        t = type(key)
        if t == str or t == Hotkey:
            key = Hotkey.keyToCode(key)
        
        t = type(key)
        if t == list:
            for i in key:
                if i not in Hotkey.__pressed:
                    Hotkey.__pressed.add(i)
        elif t == int:
            if key not in Hotkey.__pressed:
                Hotkey.__pressed.add(key)
        else:
            raise TypeError
        
    @staticmethod
    def removeFromPressedKeys(key):
        t = type(key)
        if t == str:
            key = Hotkey.keyToCode(key)
        
        t = type(key)
        if t == list:
            for i in key:
                if i in Hotkey.__pressed:
                    Hotkey.__pressed.remove(i)
        elif t == int:
            if key in Hotkey.__pressed:
                    Hotkey.__pressed.remove(key)
        else:
            raise TypeError
        
    @staticmethod
    def releaseAllKeys():
        kb = __keyboard.Controller()
        for i in Hotkey.__pressed:
            kb.release(i)
            Hotkey.__pressed.remove(i)
    
    @staticmethod
    def parse(hotkey: str) -> list:
        exclude = {' ', '+'}
        keys = []
        key = ""
        length = len(hotkey)
        for i in range(length):
            ch = hotkey[i]
            if ch not in exclude:
                key += ch
                continue
            
            if key:
                keys.append(key)
                key = ""
        
        if key:
            keys.append(key)
        return keys
    
    @staticmethod
    def keyToCode(key, force_list_return_type=False):
        t = type(key)
        if t == str:
            key = Hotkey.parse(key)
        elif t == Hotkey:
            key = key.getHotkey()
        
        t = type(key)
        if t == list:
            codes = []
            for i in key:
                t = type(i)
                if t == int:
                    codes.append(i)
                elif t == str:
                    codes.append(Hotkey.__keys[i])
                else:
                    raise TypeError
            if not force_list_return_type and len(codes) == 1:
                return codes[0]
            return codes
        else:
            return Hotkey.__keys[key]
        
    @staticmethod
    def keyToCombo(key) -> set:
        t = type(key)
        if t == str:
            key = Hotkey.parse(key)
        elif t == Hotkey:
            key = key.getHotkey()
            
        t = type(key)
        if t == list:
            combo = set()
            for i in key:
                t = type(i)
                if t == int:
                    combo.add(i)
                elif t == str:
                    combo.add(Hotkey.__keys[i])
            return combo
        
    @staticmethod
    def isKey(key) -> bool:
        t = type(key)
        if t == str:
            try:
                k = Hotkey.__keys[key]
            except KeyError:
                return False
            return True
        elif t == int:
            try:
                k = Hotkey.__keys.inverse[key]
            except KeyError:
                return False
            return True
        return False
        
class Recorder:
    class InputOption(__IntEnum):
        MOUSE = 1
        KEYBOARD = 2
        
    class MouseMovement(__IntEnum):
        ABSOLUTE = 1
        RELATIVE = 2
        
    class Hotkey(__IntEnum):
        START = 0
        PAUSE = 1
        STOP = 2
        CANCEL = 3
        
    class State(__IntEnum):
        READY = 0
        RECORDING = 1
        PLAYING = 2
        
    class InputType(__IntEnum):
        KEY = 0
        BUTTON = 1
        MOVE = 2
        SCROLL = 3
        DELAY = 4
    
    def __init__(self, start_hotkey="ctrl_l+shift_l", pause_hotkey="", stop_hotkey="ctrl_l+shift_l", cancel_hotkey="ctrl_l+z"):
        self.__record = []
        self.__state = [False, False, False]
        self.__hotkeys = [Hotkey(start_hotkey), Hotkey(pause_hotkey), Hotkey(stop_hotkey), Hotkey(cancel_hotkey)]
        self.__input_option = {self.InputOption.MOUSE, self.InputOption.KEYBOARD}
        
        # Helper variables
        self.__ready_state = -1 
        self.__prev_mouse_pos = (-1, -1)
        self.__mouse_move_counter = 0 # count the number of pixels the mouse has moved
        self.__start = 0 # start time
        self.__end = 0 # end time
        self.__delay = 0 # delay
        self.__hotkey_pos_in_record = {} # used to delete the hotkeys from record upon exiting
        for i in self.__hotkeys[self.Hotkey.START].getHotkey():
            self.__hotkey_pos_in_record[i] = -1
            
    def testHotkey(self):
        for i in self.__hotkeys:
            print("{0} | {1}".format(i.getHotkeyName(), i.getHotkeyCombo()))
    
    # Getter
    def getRecord(self) -> list:
        return self.__record
    
    def getRecordFromJson(self, file_path):
        f = open(file_path)
        data = __json.load(f)
        self.__record = data
        
    # File handling
    def saveRecordToJson(self, file_path):
        with open(file_path, "w") as f:
            f.write(__json.dumps(self.__record))
    
    # Helpers
    def __setTime(self):
        self.__end = __time.__time()
        current = self.__end - self.__start
        self.__delay = float(int((current) * 1000) / 1000)
        self.__start = __time.__time()
        
    def __removeHotkeyFromRecord(self):
        if self.InputOption.KEYBOARD not in self.__input_option: # do not pop if __keyboard not included
            return
        
        del_count = 0
        prev = 0
        for i in self.__hotkey_pos_in_record.values():
            if i < 0:
                continue
            
            index = i
            if i > prev:
                index -= del_count
                
            __log.debug("Removed hotkey at [{0}] {1}".format(index, self.__record[index]))
            del self.__record[index]
            del_count += 1
            prev = i
            
            if index < len(self.__record) and type(self.__record[index]) == float:
                __log.debug("Removed delay at [{0}] {1}".format(index, self.__record[index]))
                del self.__record[index]
                del_count += 1
                
    def isRecordEmpty(self) -> bool:
        if not self.__record:
            return True
        return False
            
    # Convertions
    @staticmethod
    def mouseToStr(button) -> str:
        if button == __mouse.Button.left:
            return "l"
        elif button == __mouse.Button.middle:
            return "m"
        elif button == __mouse.Button.right:
            return "r"
        
    @staticmethod
    def strToMouse(s):
        if s == "l":
            return __mouse.Button.left
        elif s == "m":
            return __mouse.Button.middle
        elif s == "r":
            return __mouse.Button.right  
        
    @staticmethod
    def scrollIntToStr(n) -> str:
        if n < 0:
            return "d"
        else:
            return "u"         
        
    @staticmethod
    def scrollStrToInt(s) -> int:
        if s == "u":
            return 1
        elif s == "d":
            return -1
        return 0
    
    def __speedUp(self, t: float, mult: float) -> float:
        if t < 0:
            return 0
        if mult < 0:
            return t
        
        return t * 1 / mult
    
    # Keyboard listeners
    def __onPressForReady(self, key):
        global _pressed
        start_hotkey = self.__hotkeys[self.Hotkey.START].getHotkeyCombo()
        cancel_hotkey = self.__hotkeys[self.Hotkey.CANCEL].getHotkeyCombo()
        
        if key in start_hotkey or key in cancel_hotkey:
            print("{0} | {1}".format(start_hotkey, cancel_hotkey))
            print("{0} | {1}".format(key, type(key)))
            _pressed.add(key)
            if _pressed == start_hotkey:
                self.__state[self.__ready_state] = True
                self.__ready_state = -1
                return False
            elif _pressed == cancel_hotkey:
                self.__ready_state = -1
                return False
            
            
    def __onReleaseForReady(self, key):
        global _pressed
        start_hotkey = self.__hotkeys[self.Hotkey.START].getHotkeyCombo()
        cancel_hotkey = self.__hotkeys[self.Hotkey.CANCEL].getHotkeyCombo()
        
        if key in _pressed:
            _pressed.remove(key)
            
    # def __onPressForRecord(self, key):
    #     start_hotkey = self.__hotkeys[self.Hotkey.START].getHotkeyCombo()
    #     stop_hotkey = self.__hotkeys[self.Hotkey.STOP].getHotkeyCombo()
    #     cancel_hotkey = self.__hotkeys[self.Hotkey.CANCEL].getHotkeyCombo()
        
    #     print(str(key))
    #     print(start_hotkey)
    #     print(stop_hotkey)
    #     print(cancel_hotkey)
    #     print("======")
    #     if not self.__state[self.State.RECORDING] and key not in start_hotkey and key not in cancel_hotkey:
    #         return
        
    #     if key in self.__pressed:
    #         return

    #     if self.__state[self.State.RECORDING] and self.InputOption.KEYBOARD in self.__input_option:
    #         self.__setTime()
    #         __log.info("Pressed {0}".format(key))
    #         self.__record.append(self.__delay)
    #         self.__record.append(key)
    #         if key in stop_hotkey:
    #             __log.debug("Stored hotkey position {0}".format(len(self.__record)-1))
    #             self.__hotkey_pos_in_record[key] = len(self.__record)-1
            
    #     self.__pressed.add(key)
        
    #     if not self.__state[self.State.RECORDING] and self.__pressed == cancel_hotkey:
    #         print("[END] Recording has been cancelled")
    #         return False
            
    #     if not self.__state[self.State.RECORDING] and self.__pressed == start_hotkey:
    #         self.__state[self.State.RECORDING] = True
    #         self.__pressed.clear()
            self.__prev_mouse_pos = __mouse.position
    #         print("[START] Recording input, press 'ctrl + shift' to end record")
    #         self.__start = __time.__time()
    #     elif self.__state[self.State.RECORDING] and self.__pressed == stop_hotkey:
    #         self.__state[self.State.RECORDING] = False
    #         self.__removeHotkeyFromRecord()
    #         print("[END] Recording has finished")
    #         return False
    
    # def __onReleaseForRecord(self, key):
    #     key_code = self.keyToInt(key)
    #     start_hotkey = self.__hotkeys[self.Hotkey.START].getHotkeyCombo()
        
    #     if not self.__state[self.State.RECORDING] and key_code not in start_hotkey:
    #         return
        
    #     if key_code not in self.__pressed:
    #         return

    #     if self.__state[self.State.RECORDING] and self.InputOption.KEYBOARD in self.__input_option:
    #         self.__setTime()
    #         __log.info("Released {0}".format(key))
    #         self.__record.append(self.__delay)
    #         self.__record.append(key_code)
        
    #     self.__pressed.remove(key_code)
        
    # def __onPressForPlay(self, key):
    #     key_code = self.keyToInt(key)
    #     start_hotkey = self.__hotkeys[self.Hotkey.START].getHotkeyCombo()
    #     stop_hotkey = self.__hotkeys[self.Hotkey.STOP].getHotkeyCombo()
    #     cancel_hotkey = self.__hotkeys[self.Hotkey.CANCEL].getHotkeyCombo()
        
    #     if key_code not in start_hotkey and key_code not in stop_hotkey and key_code not in cancel_hotkey:
    #         return
        
    #     if key_code in self.__pressed:
    #         return
        
    #     self.__pressed.add(key_code)
        
    #     if not self.__state[self.State.PLAYING] and self.__pressed == cancel_hotkey:
    #         print("[END] Playback has been cancelled")
    #         return False
        
    #     if not self.__state[self.State.PLAYING] and self.__pressed == start_hotkey:
    #         self.__state[self.State.PLAYING] = True
    #         self.__pressed.clear()
    #         print("[START] Playing record, press `ctrl + shift` to end playback")
    #         return False
    #     elif self.__state[self.State.PLAYING] and self.__pressed == stop_hotkey:
    #         self.__state[self.State.PLAYING] = False
    #         print("[END] Playback stopped")
    #         return False
                
    # def __onReleaseForPlay(self, key):
    #     key_code = self.keyToInt(key)
        
    #     if key_code not in self.__pressed:
    #         return
        
    #     self.__pressed.remove(key_code)

    # Mouse listeners
    # def __on_move(self, x, y):
    #     if self.InputOption.MOUSE not in self.__input_option:
    #         return 
        
    #     if not self.__state[self.State.RECORDING]:
    #         return
        
    #     if self.__mouse_move_counter < 10:
    #         self.__mouse_move_counter += 1
    #     else:
    #         self.__setTime()
    #         tup = (tuple(self.__prev_mouse_pos), self.__delay, (x, y))
    #         self.__record.append(tup)
    #         self.__mouse_move_counter = 0
    #         self.__prev_mouse_pos = (x, y)
    #         __log.info("Moved __mouse to position ({0}, {1})".format(x, y))

    # def __on_click(self, x, y, button, pressed):
    #     if self.InputOption.MOUSE not in self.__input_option:
    #         return 
        
    #     if not self.__state[self.State.RECORDING]:
    #         return
        
    #     self.__setTime()
    #     __log.info("{0} {1}".format("Pressed" if pressed else "Released", button))
    #     self.__record.append(self.__delay)
    #     self.__record.append(self.mouseToStr(button))
            
    # def __on_scroll(self, x, y, dx, dy):
    #     if self.InputOption.MOUSE not in self.__input_option:
    #         return 
        
    #     if not self.__state[self.State.RECORDING]:
    #         return
        
    #     self.__setTime()
    #     self.__record.append(self.__delay)
    #     if dy < 0:
    #         __log.info("Scrolled down")
    #         self.__record.append("d")
    #     else:
    #         __log.info("Scrolled up")
    #         self.__record.append("u")
    
    # Methods
    def record(self, option={InputOption.MOUSE, InputOption.KEYBOARD}):
        global _pressed
        if not option:
            return
        
        self.__record.clear()
        self.__input_option = option
        
        print("[READY] Press '{0}' to start recording or press '{1}' to cancel".format(self.__hotkeys[self.Hotkey.START].getHotkeyName(), self.__hotkeys[self.Hotkey.CANCEL].getHotkeyName()))
        self.__ready_state = self.State.RECORDING
        with __keyboard.Listener(on_press=self.__onPressForReady, on_release=self.__onReleaseForReady) as listener:
            listener.join()
        
        _pressed.clear()
        print("done")
        if self.__state[self.State.RECORDING]:
            print("recording")
        # with __mouse.Listener(on_move=self.__on_move, on_click=self.__on_click, on_scroll=self.__on_scroll) as listener:
        #     with __keyboard.Listener(on_press=self.__onPressForRecord, on_release=self.__onReleaseForRecord) as listener:
        #         listener.join() 
                
    # def play(self, loop=1, mouse_movement=MouseMovement.RELATIVE, speed=1.0):
    #     keyboard_controller = __keyboard.Controller()
    #     mouse_controller = __mouse.Controller()
        
    #     print("[READY] Press 'ctrl + shift' to start playback or press 'ctrl + z' to cancel")
    #     with __keyboard.Listener(on_press=self.__onPressForPlay, on_release=self.__onReleaseForPlay) as listener:
    #         listener.join()
        
    #     if not self.__state[self.State.PLAYING]:
    #         return
        
    #     key_listener = __keyboard.Listener(on_press=self.__onPressForPlay, on_release=self.__onReleaseForPlay)
    #     key_listener.start()
        
    #     length = len(self.__record)
    #     i = 0
    #     loop_count = 0
    #     while self.__state[self.State.PLAYING] and (loop < 0 or loop_count < loop):
    #         val = self.__record[i]
    #         if type(val) is int: # __keyboard
    #             key_code = self.intToKey(val)
    #             if key_code in self.__pressed:
    #                 __log.info("Releasing " + str(key_code))
    #                 keyboard_controller.release(key_code)
    #                 self.__pressed.remove(key_code)
    #             else:
    #                 __log.info("Pressing " + str(key_code))
    #                 keyboard_controller.press(key_code)
    #                 self.__pressed.add(key_code)
    #         elif type(val) is float: # delay
    #             __time.sleep(self.__speedUp(val, speed))
    #         elif type(val) is str: # __mouse buttons & scroll
    #             if val == 'l' or val == 'm' or val == 'r':
    #                 if val in self.__pressed:
    #                     __log.info("Releasing " + val)
    #                     mouse_controller.release(self.strToMouse(val))
    #                     self.__pressed.remove(val)
    #                 else:
    #                     __log.info("Pressing " + val)
    #                     mouse_controller.press(self.strToMouse(val))
    #                     self.__pressed.add(val)
    #             elif val == 'u' or val == 'd':
    #                 mouse_controller.scroll(0, self.scrollStrToInt(val))
    #         else: # __mouse movement
    #             if mouse_movement == self.MouseMovement.RELATIVE:
    #                 current_mouse_pos = tuple(__mouse.position)
    #                 rel_x = current_mouse_pos[0] + (val[2][0] - val[0][0])
    #                 rel_y = current_mouse_pos[1] + (val[2][1] - val[0][1])
    #                 __time.sleep(self.__speedUp(val[1], speed))
    #                 mouse_controller.position = (rel_x, rel_y)
    #                 __log.info("Moved __mouse to position ({0}, {1})".format(rel_x, rel_y))
    #             else:
    #                 mouse_controller.position = (val[0][0], val[0][1])
    #                 __time.sleep(self.__speedUp(val[1], speed))
    #                 mouse_controller.position = (val[2][0], val[2][1])
    #                 __log.info("Moved __mouse to position ({0}, {1})".format(val[2][0], val[2][1]))
    #         i += 1
    #         if i >= length and (loop < 0 or loop_count < loop):
    #             i = 0
    #             loop_count += 1
                
    #     key_listener.stop()
    #     if self.__state[self.State.PLAYING] == True:
    #         self.__state[self.State.PLAYING] = False
    #         print("[END] Playback finished")
         
    #     self.__pressed.clear()
    
    def __show_key(self, key):
        try:
            key_code = key.vk
        except AttributeError:
            key_code = key.value.vk
        print(str(key) + " | " + str(key_code))
        
    def test(self):
        listener = __keyboard.Listener(on_press=self.__show_key)
        listener.start()
        try:
            while listener.is_alive():
                __time.sleep(1)
        except KeyboardInterrupt:
            listener.stop()
                
    def printRecord(self):
        for i in range(len(self.__record)):
            val = self.__record[i]
            if type(val) == int:
                if val in self.__pressed:
                    print("[{0}] Released {1}".format(i, val))
                    self.__pressed.remove(val)
                else:
                    print("[{0}] Pressed {1}".format(i, val))
                    self.__pressed.add(val)
            elif type(val) == float:
                print("[{0}] Delay {1}s".format(i, val))
            elif type(val) == str:
                if val == 'l' or val == 'm' or val == 'r':
                    if val in self.__pressed: 
                        print("[{0}] Released {1}".format(i, val))
                        self.__pressed.remove(val)
                    else:
                        print("[{0}] Pressed {1}".format(i, val))
                        self.__pressed.add(val)
                elif val == 'u' or val == 'd':
                    print("[{0}] Scrolled {1}".format(i, "down" if val == "d" else "up"))
            else:
                print("[{0}] {1}".format(i, val))
        print("Length: {0}".format(len(self.__record)))
        self.__pressed.clear()
            
    def printTypes(self):
        for i in self.__record:
            print(type(i))
        
def strToJson(s: str) -> str:
    if s.endswith(".__json"):
        return s
    return s + ".__json"

def strToMouseMovement(s: str):
    s = s.lower()
    if s.startswith("abs"):
        return Recorder.MouseMovement.ABSOLUTE
    elif s.startswith("rel"):
        return Recorder.MouseMovement.RELATIVE

def addRecord(args, record_dir):
    record_dir = __path(record_dir)
    if not record_dir.exists():
        record_dir.mkdir(parents=True)
        
    input = Recorder()
    input_option = set()
    record_name = strToJson(args.record)
    if args.__mouse:
        input_option.add(Recorder.InputOption.MOUSE)
    if args.__keyboard:
        input_option.add(Recorder.InputOption.KEYBOARD)
    
    if not input_option:
        print("[ERROR] Input option cannot be empty, try adding either '-m' or '-k' flag")
        return
    
    input.record(option=input_option)
    if not input.isRecordEmpty():
        input.saveRecordToJson(record_dir.joinpath(record_name))
    
def removeRecord(args, record_dir):
    record_dir = __path(record_dir)
    files = args.record
    for i in files:  
        file = record_dir.joinpath(strToJson(i))
        if file.exists():
            file.unlink()
            print("[SUCCESS] Deleted record {0}".format(file.stem))
    
def listRecords(path):
    path = __path(path)
    if not path.exists():
        print("[ERROR] Record directory does not exist")
        return
        
    print("Records:")
    files = path.glob('*')
    for file in files:
        print("  " + file.stem)
        
def playRecord(args, record_dir):
    record_dir = __path(record_dir)
    input = Recorder()
    record_name = str(record_dir.joinpath(strToJson(args.record)))
    input.getRecordFromJson(record_name)
    input.play(args.loop, strToMouseMovement(args.movement), args.speed)
    
def readConfig(config_path) -> dict:
    with open(config_path, 'r') as file:
        data = __json.load(file)
    return data

def writeConfig(config, config_path):
    data = __json.dumps(config, indent=4)
    with open(config_path, 'w') as file:
        file.write(data)

def main():
    current_dir = __path(__file__).parent.resolve()
    config_path = current_dir.joinpath("config.__json")
    config = {"recordDirectory" : str(current_dir.joinpath("records"))}

    

    # if not config_path.exists():
    #     writeConfig(config, config_path)
    # else:
    #     config = readConfig(config_path)
        
    # record_dir = config["recordDirectory"]
    
    # # main
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-v", "--version", action="version", version="%(prog)s {0}".format("0.1.1-alpha"))
    # subparser = parser.add_subparsers(dest="command1")
    
    # # record
    # cmd_record = subparser.add_parser("record", help="record input")
    # record_subparser = cmd_record.add_subparsers(dest="command2")
    
    # # record add
    # cmd_record_add = record_subparser.add_parser("add", help="add a new record")
    # cmd_record_add.add_argument("record", type=str)
    # cmd_record_add.add_argument("-m", "--__mouse", action="store_true", dest="__mouse", help="enable __mouse when recording")
    # cmd_record_add.add_argument("-k", "--__keyboard", action="store_true", dest="__keyboard", help="enable __keyboard when recording")
    
    # # record remove
    # cmd_record_remove = record_subparser.add_parser("remove", help="delete record(s)")
    # cmd_record_remove.add_argument("record", nargs='+', type=str, help="a list of records")
    
    # # record list
    # cmd_record_list = record_subparser.add_parser("list", help="list all records")
    
    # # play
    # cmd_play = subparser.add_parser("play", help="play a record")
    # cmd_play.add_argument("record", nargs='?', help="the record to play")
    # cmd_play.add_argument("-a", "--all", action="store_true", dest="all", help="list all records")
    # cmd_play.add_argument("--loop", nargs='?', type=int, default=1, const=-1, dest="loop", help="loop playback")
    # cmd_play.add_argument("-s", "--speed", nargs='?', type=float, default=1, dest="speed", help="speed multiplier for the playback")
    # cmd_play.add_argument("-m", "--movement", nargs='?', type=str, default="rel", dest="movement", help="the type of __mouse movement to use (absolute or relative)")
    
    # # config
    # cmd_config = subparser.add_parser("config", help="config settings")
    # config_subparser = cmd_config.add_subparsers(dest="command2")
    
    # # config set
    # cmd_config_set = config_subparser.add_parser("set", help="set config settings")
    # cmd_config_set.add_argument("config", nargs=2, type=str, help="the config to change to a new value")
    
    # # config get
    # cmd_config_get = config_subparser.add_parser("get", help="get config values")
    # cmd_config_get.add_argument("config", nargs='*', type=str, help="the config values to get")
    
    # args = parser.parse_args("record add test -mk".split(" "))
    # if args.command1 == "record":
    #     if args.command2 == "add":
    #         addRecord(args, record_dir)
    #     elif args.command2 == "remove":
    #         removeRecord(args, record_dir)
    #     elif args.command2 == "list":
    #         listRecords(record_dir)
    # elif args.command1 == "play":
    #     if args.all:
    #         listRecords(record_dir)
    #         exit()
    #     playRecord(args, record_dir)
    # elif args.command1 == "config":
    #     if args.command2 == "set":
    #         key = args.config[0]
    #         val = args.config[1]
    #         if key in config:
    #             config[key] = val
    #             writeConfig(config, config_path)
    #             print("[SUCCESS] Config setting \"{0}\" has been set to \"{1}\"".format(key, val))
    #         else:
    #             print("[ERROR] Config setting \"{0}\" does not exist".format(key))
    #     elif args.command2 == "get":
    #         if not args.config:
    #             for k, v in config.items():
    #                 print("\"{0}\": \"{1}\"".format(k, v))
    #         else:
    #             for i in args.config:
    #                 if i in config:
    #                     print("\"{0}\": \"{1}\"".format(i, config[i]))
    #                 else: 
    #                     print("[ERROR] Config setting \"{0}\" does not exist".format(i))
    
if __name__ == "__main__":
    main()
    
# __keyboard = int
# __time = float
# scroll = str(u | d)
# __mouse movement = tuple(3)
# __mouse button = str(l | m | r)