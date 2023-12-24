import argparse as __argparse
import time as _time
import logging as _logging
import json as _json
from enum import IntEnum as _IntEnum
from pathlib import Path as _path
from pynput import mouse as _mouse
from pynput import keyboard as _keyboard
from bidict import bidict as __bidict

_logging.basicConfig(format="[%(levelname)s] %(message)s")
_log = _logging.getLogger()
_log.setLevel(_logging.DEBUG)

_pressed = set()
__keys = __bidict({'\"': 222, '*': 106, '+': 107, ',': 188, '-': 109, '.': 190, '/': 191, '0': 48, '1': 49, '2': 50, '3': 51, '4': 52, 
    '5': 53, '6': 54, '7': 55, '8': 56, '9': 57, ';': 186, '<100>': 100, '<101>': 101, '<102>': 102, '<103>': 103, 
    '<104>': 104, '<105>': 105, '<110>': 110, '<96>': 96, '<97>': 97, '<98>': 98, '<99>': 99, '=': 187, "alt_r": 165,
    "alt": 164, "backspace": 8, "caps_lock": 20, "cmd": 91, "ctrl": 162, "ctrl_r": 163, 
    "delete": 46, "down": 40, "enter": 13, "esc": 27, "f1": 112, "f10": 121, "f11": 122, 
    "f12": 123, "f2": 113, "f3": 114, "f4": 115, "f5": 116, "f6": 117, "f7": 118, "f8": 119, 
    "f9": 120, "insert": 45, "left": 37, "media_next": 176, "media_play_pause": 179, 
    "media_previous": 177, "media_volume_down": 174, "media_volume_mute": 173, "media_volume_up": 175, 
    "num_lock": 144, "print_screen": 44, "right": 39, "shift": 160, "shift_r": 161, "space": 32, 
    "tab": 9, "up": 38, '[': 219, '\\': 220, ']': 221, '`': 192, 'a': 65, 'b': 66, 'c': 67, 'd': 68, 'e': 69, 
    'f': 70, 'g': 71, 'h': 72, 'i': 73, 'j': 74, 'k': 75, 'l': 76, 'm': 77, 'n': 78, 'o': 79, 'p': 80, 'q': 81, 'r': 82, 
    's': 83, 't': 84, 'u': 85, 'v': 86, 'w': 87, 'x': 88, 'y': 89, 'z': 90})
__buttons = __bidict({"LMB": _mouse.Button.left, "MMB": _mouse.Button.middle, "RMB": _mouse.Button.right, 
                      "X1": _mouse.Button.x1, "X2": _mouse.Button.x2})

class Hotkey:
    def __init__(self, hotkey="") -> None:
        self.__hotkey = []
        self.__hotkey_combo = set()
        self.setHotkey(hotkey)
        
    def getHotkey(self):
        return self.__hotkey
        
    def getHotkeyName(self):
        return Hotkey.join(self.__hotkey)
    
    def getHotkeyCombo(self):
        return self.__hotkey_combo
    
    def setHotkey(self, hotkey):
        if type(hotkey) == str:
            self.__hotkey = Hotkey.parse(hotkey)
        elif type(hotkey) == list:
            for i in hotkey:
                if type(i) == str:
                    self.__hotkey.append(i)
        
        self.__hotkey_combo = toCombo(self.__hotkey)
        
    def setHotkeyFromInput(self):
        self.__hotkey.clear()
        self.__hotkey_combo.clear()
        with _keyboard.Listener(on_press=self.__onPress, on_release=self.__onRelease) as listener:    
            listener.join()
        
    def __onPress(self, key):
        key_code = toKeyCode(key)
        if key_code not in _pressed:
            if _keyboard.Key.ctrl_l.value.vk in _pressed:
                print("ctrl pressed")
                _keyboard.Controller().release(_keyboard.Key.ctrl_l)
            _pressed.add(key_code)
            self.__hotkey.append(key)
            self.__hotkey_combo.add(key_code)
            
    def __onRelease(self, key):
        if key == _keyboard.Key.ctrl_l:
            return
        _pressed.clear()
        return False
    
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
                if not isKeyString(key):
                    raise KeyError("Unknown Key: '{0}'".format(key))
                keys.append(key)
                key = ""
        
        if key:
            if not isKeyString(key):
                raise KeyError("Unknown Key: '{0}'".format(key))
            keys.append(key)
        return keys
    
    @staticmethod
    def join(hotkey: list) -> str:
        name = ""
        length = len(hotkey)
        for i in range(length):
            key = hotkey[i]
            name += key
            if i < length-1:
                name += " + "
        return name
    
def __convertKeyCode(char_key: _keyboard.KeyCode):
    global __keys
    key_code = char_key.vk
    if key_code == None:
        key_code = char_key.char
        return __keys[key_code]
    return key_code
    
def toString(input) -> str:
    global __keys
    t = type(input)
    inputs = []
    if t == list:
        inputs += input
    else:
        inputs.append(input)
    
    global __keys
    global __buttons
    names = []
    for i in inputs:
        t = type(i)
        if t == int:
            names.append(__keys.inverse[i])
        elif t == _keyboard.Key:
            names.append(__keys.inverse[i.value.vk])
        elif t == _keyboard.KeyCode:
            names.append(__keys.inverse[__convertKeyCode(i)])
        elif t == _mouse.Button:
            names.append(__buttons.inverse[i])
        else:
            raise TypeError
    return Hotkey.join(names)
    
def toKeyCode(key, force_list_return_type=False):
    t = type(key)
    if t == str:
        key = Hotkey.parse(key)
    elif t == Hotkey:
        key = key.getHotkey()
    elif t == int:
        return key
    elif t == _keyboard.KeyCode:
        return __convertKeyCode(key)
    elif t == _keyboard.Key:
        return key.value.vk
    
    global __keys
    t = type(key)
    if t == list:
        codes = []
        for i in key:
            t = type(i)
            if t == int:
                codes.append(i)
            elif t == str:
                codes.append(__keys[i])
            elif t == _keyboard.KeyCode:
                codes.append(__convertKeyCode(i))
            elif t == _keyboard.Key:
                codes.append(i.value.vk)
            else:
                raise TypeError
        if not force_list_return_type and len(codes) == 1:
            return codes[0]
        return codes
    else:
        raise TypeError
    
def toCombo(key) -> set:
    key = toKeyCode(key)
    combo = set()
    for i in key:
        combo.add(i)
    return combo
    
def toKey(key, force_list_return_type=False):
    key = toKeyCode(key, True)
    keys = []
    for i in key:
        keys.append(_keyboard.KeyCode.from_vk(i))
    if not force_list_return_type and len(keys) == 1:
        return keys[0]
    return keys

def toButton(button: str):
    global __buttons
    return __buttons[button]

def isKeyString(key: str) -> bool:
    global __keys
    if key in __keys:
        return True
    return False

def isKeyCode(key_code: int) -> bool:
    global __keys
    if key_code in __keys.inverse:
        return True
    return False
        
def isKey(key) -> bool:
    global __keys
    t = type(key)
    if t == _keyboard.Key or t == _keyboard.KeyCode:
        return True
    return False

def isButtonString(button: str) -> bool:
    global __buttons
    if button in __buttons:
        return True
    return False

def isButton(button) -> bool:
    global __buttons
    if type(button) == _mouse.Button:
        return True
    return False
        
class Recorder:
    class InputOption(_IntEnum):
        MOUSE = 0
        KEYBOARD = 1
        
    class MouseMovement(_IntEnum):
        ABSOLUTE = 0
        RELATIVE = 1
        
    class Hotkey(_IntEnum):
        START = 0
        PAUSE = 1
        STOP = 2
        CANCEL = 3
        
    class State(_IntEnum):
        READY = 0
        RECORDING = 1
        PLAYING = 2
        
    class InputType(_IntEnum):
        KEY = 0
        BUTTON = 1
        MOVE = 2
        SCROLL = 3
        DELAY = 4
    
    def __init__(self, start_hotkey="ctrl+shift", pause_hotkey="", stop_hotkey="ctrl+shift", cancel_hotkey="ctrl+z"):
        self.__record = []
        self.__states = [False, False, False]
        self.__hotkeys = [Hotkey(start_hotkey), Hotkey(pause_hotkey), Hotkey(stop_hotkey), Hotkey(cancel_hotkey)]
        self.__input_option = {self.InputOption.MOUSE, self.InputOption.KEYBOARD}
        
        # Helper variables
        self.__ready_state = -1 
        self.__mouse_move_counter = 0 # count the number of pixels the mouse has moved
        self.__start = 0 # start time
        self.__end = 0 # end time
        self.__delay = 0 # delay
        self.__hotkey_pos_in_record = {} # used to delete the hotkeys from record upon exiting
        for i in self.__hotkeys[self.Hotkey.STOP].getHotkey():
            self.__hotkey_pos_in_record[i] = -1
    
    # Getter
    def getRecord(self) -> list:
        return self.__record
    
    def getRecordFromJson(self, file_path):
        f = open(file_path)
        data = _json.load(f)
        self.__record = data
        
    # File handling
    def saveRecordToJson(self, file_path):
        with open(file_path, "w") as f:
            f.write(_json.dumps(self.__record))
    
    # Helpers
    def __setTime(self):
        self.__end = _time.time()
        current = self.__end - self.__start
        self.__delay = float(int((current) * 1000) / 1000)
        self.__start = _time.time()
        
    def __removeHotkeyFromRecord(self):        
        del_count = 0
        prev = 0
        indices = list(self.__hotkey_pos_in_record.values())
        for i in indices:
            if i < 0:
                continue
            
            index = i
            if i > prev:
                index -= del_count
                
            _log.debug("Removed hotkey at [{0}] {1}".format(index, self.__record[index]))
            del self.__record[index]
            del_count += 1
            prev = i
            
            if index < len(self.__record) and self.__record[index][0] == self.InputType.DELAY:
                _log.debug("Removed delay at [{0}] {1}".format(index, self.__record[index]))
                del self.__record[index]
                del_count += 1
                
    def isRecordEmpty(self) -> bool:
        if not self.__record:
            return True
        return False
    
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
        key_code = toKeyCode(key)
        if key_code in start_hotkey or key_code in cancel_hotkey:
            _pressed.add(key_code)
            if _pressed == start_hotkey:
                self.__states[self.__ready_state] = True
                self.__ready_state = -1
                return False
            elif _pressed == cancel_hotkey:
                self.__ready_state = -1
                return False
            
    def __onReleaseForReady(self, key):
        global _pressed
        if key in _pressed:
            _pressed.remove(key)
            
    def __onPressForRecord(self, key):
        stop_hotkey = self.__hotkeys[self.Hotkey.STOP].getHotkeyCombo()
        key_code = toKeyCode(key)
        if self.InputOption.KEYBOARD not in self.__input_option and key_code not in stop_hotkey:
            return
        
        global _pressed
        if key_code in _pressed:
            return
        
        _pressed.add(key_code)
        
        key_string = toString(key_code)
        _log.info("Pressed '{0}'".format(key_string))
        self.__setTime()
        self.__record.append(tuple([self.InputType.DELAY, self.__delay]))
        self.__record.append(tuple([self.InputType.KEY, key_string]))
        if key_code in stop_hotkey:
            self.__hotkey_pos_in_record[key_string] = len(self.__record)-1
            
        if _pressed == stop_hotkey:
            self.__removeHotkeyFromRecord()
            print("[END] Recording stopped")
            return False
    
    def __onReleaseForRecord(self, key):
        stop_hotkey = self.__hotkeys[self.Hotkey.STOP].getHotkeyCombo()
        key_code = toKeyCode(key)
        if self.InputOption.KEYBOARD not in self.__input_option and key_code not in stop_hotkey:
            return
        
        global _pressed
        if key_code not in _pressed:
            return
    
        _pressed.remove(key_code)
        
        key_string = toString(key_code)
        self.__setTime()
        _log.info("Released '{0}'".format(key_string))
        self.__record.append(tuple([self.InputType.DELAY, self.__delay]))
        self.__record.append(tuple([self.InputType.KEY, key_string]))
        
    def __onPressForPlay(self, key):
        global _pressed
        key_code = toKeyCode(key)
        
        if key_code in _pressed:
            return
        
        stop_hotkey = self.__hotkeys[self.Hotkey.STOP].getHotkeyCombo()
        _pressed.add(key_code)
        
        if _pressed == stop_hotkey:
            self.__states[self.State.PLAYING] = False
            print("[END] Playback stopped")
            return False
                
    def __onReleaseForPlay(self, key):
        global _pressed
        key_code = toKeyCode(key)
        
        if key_code not in _pressed:
            return
    
        _pressed.remove(key_code)

    # Mouse listeners
    def __onMoveForRecord(self, x, y):
        if self.InputOption.MOUSE not in self.__input_option:
            return 
        
        if self.__mouse_move_counter < 10:
            self.__mouse_move_counter += 1
        else:
            mouse_pos = _mouse.Controller().position
            self.__setTime()
            self.__record.append(tuple([self.InputType.DELAY, self.__delay]))
            self.__record.append(tuple([self.InputType.MOVE, tuple([mouse_pos[0], mouse_pos[1]])]))
            self.__mouse_move_counter = 0
            _log.info("Moved mouse to position ({0}, {1})".format(mouse_pos[0], mouse_pos[1]))

    def __onClickForRecord(self, x, y, button, pressed):
        if self.InputOption.MOUSE not in self.__input_option:
            return 
        
        global _pressed
        button_string = toString(button)
        
        in_pressed = button_string in _pressed
        if pressed:
            if not in_pressed:
                _pressed.add(button_string)
            else:
                return
        else:
            if in_pressed:
                _pressed.remove(button_string)
            else:
                return
        
        self.__setTime()
        _log.info("{0} {1}".format("Pressed" if pressed else "Released", button))
        self.__record.append(tuple([self.InputType.DELAY, self.__delay]))
        self.__record.append(tuple([self.InputType.BUTTON, button_string]))
            
    def __onScrollForRecord(self, x, y, dx, dy):
        if self.InputOption.MOUSE not in self.__input_option:
            return 
        
        self.__setTime()
        self.__record.append(tuple([self.InputType.DELAY, self.__delay]))
        self.__record.append(tuple([self.InputType.SCROLL, dy]))
        if dy < 0:
            _log.info("Scrolled down")
        else:
            _log.info("Scrolled up")
    
    # Methods
    def record(self, option={InputOption.MOUSE, InputOption.KEYBOARD}):
        global _pressed
        if not option:
            return
        
        self.__record.clear()
        self.__input_option = option
        
        print("[READY] Press '{0}' to start recording or press '{1}' to cancel".format(self.__hotkeys[self.Hotkey.START].getHotkeyName(), self.__hotkeys[self.Hotkey.CANCEL].getHotkeyName()))
        self.__ready_state = self.State.RECORDING
        with _keyboard.Listener(on_press=self.__onPressForReady, on_release=self.__onReleaseForReady) as listener:
            listener.join()

        _pressed.clear()
        
        if not self.__states[self.State.RECORDING]:
            print("[END] Recording cancelled")
            return
        
        print("[START] Press '{0}' to end recording".format(self.__hotkeys[self.Hotkey.STOP].getHotkeyName()))
        with _mouse.Listener(on_move=self.__onMoveForRecord, on_click=self.__onClickForRecord, on_scroll=self.__onScrollForRecord) as listener:
            with _keyboard.Listener(on_press=self.__onPressForRecord, on_release=self.__onReleaseForRecord) as listener:
                self.__start = _time.time()
                listener.join() 
                
        _pressed.clear()
        self.__states[self.State.RECORDING] = False
                
    def play(self, loop=1, mouse_movement=MouseMovement.RELATIVE, speed=1.0):
        keyboard_controller = _keyboard.Controller()
        mouse_controller = _mouse.Controller()
        
        self.__ready_state = self.State.PLAYING
        print("[READY] Press '{0}' to start playback or press '{1}' to cancel".format(self.__hotkeys[self.Hotkey.START].getHotkeyName(), self.__hotkeys[self.Hotkey.CANCEL].getHotkeyName()))
        with _keyboard.Listener(on_press=self.__onPressForReady, on_release=self.__onReleaseForReady) as listener:
            listener.join()
        
        if not self.__states[self.State.PLAYING]:
            print("[END] Playback cancelled")
            return
        
        print("[START] Press '{0}' to stop playback".format(self.__hotkeys[self.Hotkey.STOP].getHotkeyName()))
        key_listener = _keyboard.Listener(on_press=self.__onPressForPlay, on_release=self.__onReleaseForPlay)
        key_listener.start()
        
        pressed_in_playback = set()
        prev_mouse_pos = (-1, -1)
        length = len(self.__record)
        i = 0
        loop_count = 0
        while self.__states[self.State.PLAYING] and (loop < 0 or loop_count < loop):
            val = self.__record[i]
            input_type = val[0]
            if input_type == self.InputType.DELAY:
                _time.sleep(self.__speedUp(val[1], speed))
            elif input_type == self.InputType.MOVE:
                if mouse_movement == self.MouseMovement.RELATIVE:
                    if prev_mouse_pos == (-1, -1):
                        prev_mouse_pos = val[1]
                        continue
                    mouse_pos = val[1]
                    mouse_controller.move(mouse_pos[0] - prev_mouse_pos[0], mouse_pos[1] - prev_mouse_pos[1])
                    prev_mouse_pos = mouse_pos
                else:
                    mouse_controller.position = (val[1][0], val[1][1])
                _log.info("Moved mouse to position ({0}, {1})".format(mouse_controller.position[0], mouse_controller.position[1]))
            elif input_type == self.InputType.KEY:
                if val[1] not in pressed_in_playback:
                    pressed_in_playback.add(val[1])
                    keyboard_controller.press(toKey(val[1]))
                    _log.info("Pressed '{0}'".format(val[1]))
                else:
                    pressed_in_playback.remove(val[1])
                    keyboard_controller.release(toKey(val[1]))
                    _log.info("Released '{0}'".format(val[1]))
            elif input_type == self.InputType.SCROLL:
                mouse_controller.scroll(0, val[1])
                _log.info("Scrolled {0}".format("up" if val[1] > 0 else "down"))
            elif input_type == self.InputType.BUTTON:
                if val[1] not in pressed_in_playback:
                    pressed_in_playback.add(val[1])
                    mouse_controller.press(toButton(val[1]))
                    _log.info("Pressed '{0}'".format(val[1]))
                else:
                    pressed_in_playback.remove(val[1])
                    mouse_controller.release(toButton(val[1]))
                    _log.info("Released '{0}'".format(val[1]))
            i += 1
            if i >= length and (loop < 0 or loop_count < loop):
                i = 0
                loop_count += 1
                prev_mouse_pos = (-1, -1)
                
        key_listener.stop()
        if self.__states[self.State.PLAYING]:
            self.__states[self.State.PLAYING] = False
            print("[END] Playback finished")
         
        _pressed.clear()
    
    # def __show_key(self, key):
    #     try:
    #         key_code = key.vk
    #     except AttributeError:
    #         key_code = key.value.vk
    #     print(str(key) + " | " + str(key_code))
        
    # def test(self):
    #     listener = _keyboard.Listener(on_press=self.__show_key)
    #     listener.start()
    #     try:
    #         while listener.is_alive():
    #             _time.sleep(1)
    #     except KeyboardInterrupt:
    #         listener.stop()
                
    def printRecord(self):
        for i in range(len(self.__record)):
            val = self.__record[i]
            if val[0] == self.InputType.KEY:
                print("[{0}] Key: {1}".format(i, val[1]))
            elif val[0] == self.InputType.BUTTON:
                print("[{0}] Button: {1}".format(i, val[1]))
            elif val[0] == self.InputType.MOVE:
                print("[{0}] Moved mouse to: ({1}, {2})".format(i, val[1][0], val[1][1]))
            elif val[0] == self.InputType.SCROLL:
                print("[{0}] Scroll {1}".format(i, "up" if val[1] > 0 else "down"))
            elif val[0] == self.InputType.DELAY:
                print("[{0}] Delay: {1}s".format(i, val[1]))    
        print("Length: {0}".format(len(self.__record)))
        
def __strToJson(s: str) -> str:
    if s.endswith(".json"):
        return s
    return s + ".json"

def __strToMouseMovement(s: str):
    s = s.lower()
    if s.startswith("abs"):
        return Recorder.MouseMovement.ABSOLUTE
    elif s.startswith("rel"):
        return Recorder.MouseMovement.RELATIVE

def __addRecord(args, record_dir):
    record_dir = _path(record_dir)
    if not record_dir.exists():
        record_dir.mkdir(parents=True)
        
    input = Recorder()
    input_option = set()
    record_name = __strToJson(args.record)
    if args._mouse:
        input_option.add(Recorder.InputOption.MOUSE)
    if args._keyboard:
        input_option.add(Recorder.InputOption.KEYBOARD)
    
    if not input_option:
        print("[ERROR] Input option cannot be empty, try adding either '-m' or '-k' flag")
        return
    
    input.record(option=input_option)
    if not input.isRecordEmpty():
        input.saveRecordToJson(record_dir.joinpath(record_name))
    
def __removeRecord(args, record_dir):
    record_dir = _path(record_dir)
    files = args.record
    for i in files:  
        file = record_dir.joinpath(__strToJson(i))
        if file.exists():
            file.unlink()
            print("[SUCCESS] Deleted record {0}".format(file.stem))
    
def __listRecords(path):
    path = _path(path)
    if not path.exists():
        print("[ERROR] Record directory does not exist")
        return
        
    print("Records:")
    files = path.glob('*')
    for file in files:
        print("  " + file.stem)
        
def __playRecord(args, record_dir):
    record_dir = _path(record_dir)
    input = Recorder()
    record_name = str(record_dir.joinpath(__strToJson(args.record)))
    input.getRecordFromJson(record_name)
    input.play(args.loop, __strToMouseMovement(args.movement), args.speed)
    
def __readConfig(config_path) -> dict:
    with open(config_path, 'r') as file:
        data = _json.load(file)
    return data

def __writeConfig(config, config_path):
    data = _json.dumps(config, indent=4)
    with open(config_path, 'w') as file:
        file.write(data)

def main():
    current_dir = _path(__file__).parent.resolve()
    config_path = current_dir.joinpath("config.json")
    config = {"recordDirectory" : str(current_dir.joinpath("records"))}
    
    if not config_path.exists():
        __writeConfig(config, config_path)
    else:
        config = __readConfig(config_path)
        
    record_dir = config["recordDirectory"]
    
    # main
    parser = __argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version="%(prog)s {0}".format("0.2.0-alpha"))
    subparser = parser.add_subparsers(dest="command1")
    
    # record
    cmd_record = subparser.add_parser("record", help="record input")
    record_subparser = cmd_record.add_subparsers(dest="command2")
    
    # record add
    cmd_record_add = record_subparser.add_parser("add", help="add a new record")
    cmd_record_add.add_argument("record", type=str)
    cmd_record_add.add_argument("-m", "--_mouse", action="store_true", dest="_mouse", help="enable mouse when recording")
    cmd_record_add.add_argument("-k", "--_keyboard", action="store_true", dest="_keyboard", help="enable keyboard when recording")
    
    # record remove
    cmd_record_remove = record_subparser.add_parser("remove", help="delete record(s)")
    cmd_record_remove.add_argument("record", nargs='+', type=str, help="a list of records")
    
    # record list
    cmd_record_list = record_subparser.add_parser("list", help="list all records")
    
    # play
    cmd_play = subparser.add_parser("play", help="play a record")
    cmd_play.add_argument("record", nargs='?', help="the record to play")
    cmd_play.add_argument("-a", "--all", action="store_true", dest="all", help="list all records")
    cmd_play.add_argument("--loop", nargs='?', type=int, default=1, const=-1, dest="loop", help="loop playback")
    cmd_play.add_argument("-s", "--speed", nargs='?', type=float, default=1, dest="speed", help="speed multiplier for the playback")
    cmd_play.add_argument("-m", "--movement", nargs='?', type=str, default="rel", dest="movement", help="the type of _mouse movement to use (absolute or relative)")
    
    # config
    cmd_config = subparser.add_parser("config", help="config settings")
    config_subparser = cmd_config.add_subparsers(dest="command2")
    
    # config set
    cmd_config_set = config_subparser.add_parser("set", help="set config settings")
    cmd_config_set.add_argument("config", nargs=2, type=str, help="the config to change to a new value")
    
    # config get
    cmd_config_get = config_subparser.add_parser("get", help="get config values")
    cmd_config_get.add_argument("config", nargs='*', type=str, help="the config values to get")
    
    args = parser.parse_args()
    if args.command1 == "record":
        if args.command2 == "add":
            __addRecord(args, record_dir)
        elif args.command2 == "remove":
            __removeRecord(args, record_dir)
        elif args.command2 == "list":
            __listRecords(record_dir)
    elif args.command1 == "play":
        if args.all:
            __listRecords(record_dir)
            exit()
        __playRecord(args, record_dir)
    elif args.command1 == "config":
        if args.command2 == "set":
            key = args.config[0]
            val = args.config[1]
            if key in config:
                config[key] = val
                __writeConfig(config, config_path)
                print("[SUCCESS] Config setting \"{0}\" has been set to \"{1}\"".format(key, val))
            else:
                print("[ERROR] Config setting \"{0}\" does not exist".format(key))
        elif args.command2 == "get":
            if not args.config:
                for k, v in config.items():
                    print("\"{0}\": \"{1}\"".format(k, v))
            else:
                for i in args.config:
                    if i in config:
                        print("\"{0}\": \"{1}\"".format(i, config[i]))
                    else: 
                        print("[ERROR] Config setting \"{0}\" does not exist".format(i))
    
if __name__ == "__main__":
    main()
    
# Bugs