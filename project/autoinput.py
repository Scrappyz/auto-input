import time
import logging
import json
import argparse
from enum import Enum
from enum import IntEnum
from os import getcwd
from pyautogui import position as currentMousePosition
from pathlib import Path
from pynput import mouse
from pynput import keyboard

logging.basicConfig(format="[%(levelname)s] %(message)s")
log = logging.getLogger()
log.setLevel(logging.INFO)

class Input:
    class InputOption(Enum):
        MOUSE = 1
        KEYBOARD = 2
        
    class MouseMovement(Enum):
        ABSOLUTE = 1
        RELATIVE = 2
        
    class Hotkey(IntEnum):
        START = 0
        PAUSE = 1
        STOP = 2
        CANCEL = 3
        
    class State(IntEnum):
        READY = 0
        RECORDING = 1
        PLAYING = 2
    
    def __init__(self):
        self.__record = []
        self.__state = [False, False, False]
        self.__hotkeys = [{162, 160}, {}, {162, 160}, {162, 90}]
        self.__input_option = {self.InputOption.MOUSE, self.InputOption.KEYBOARD}
        
        # Helper variables
        self.__pressed = set() # keep track of pressed buttons
        self.__prev_mouse_pos = (-1, -1)
        self.__mouse_move_counter = 0 # count the number of pixels the mouse has moved
        self.__start = 0 # start time
        self.__end = 0 # end time
        self.__delay = 0 # delay
        self.__hotkey_pos_in_record = {} # used to delete the hotkeys from record upon exiting
        for i in self.__hotkeys[self.Hotkey.START]:
            self.__hotkey_pos_in_record[i] = -1
    
    # Getter
    def getRecord(self) -> list:
        return self.__record
    
    def getRecordFromJson(self, file_path):
        f = open(file_path)
        data = json.load(f)
        self.__record = data
        
    # File handling
    def saveRecordToJson(self, file_path):
        with open(file_path, "w") as f:
            f.write(json.dumps(self.__record))
    
    # Helpers
    def __setTime(self):
        self.__end = time.time()
        current = self.__end - self.__start
        self.__delay = float(int((current) * 1000) / 1000)
        self.__start = time.time()
        
    def __removeHotkeyFromRecord(self):
        if self.InputOption.KEYBOARD not in self.__input_option: # do not pop if keyboard not included
            return
        
        del_count = 0
        prev = 0
        for i in self.__hotkey_pos_in_record.values():
            if i < 0:
                continue
            
            index = i
            if i > prev:
                index -= del_count
                
            log.debug("Removed hotkey at [{0}] {1}".format(index, self.__record[index]))
            del self.__record[index]
            del_count += 1
            prev = i
            
            if index < len(self.__record) and type(self.__record[index]) == float:
                log.debug("Removed delay at [{0}] {1}".format(index, self.__record[index]))
                del self.__record[index]
                del_count += 1
                
    def isRecordEmpty(self) -> bool:
        if not self.__record:
            return True
        return False
            
    # Convertions
    @staticmethod
    def keyToInt(key) -> int:
        try:
            key_code = key.vk
        except AttributeError:
            key_code = key.value.vk
        return key_code
    
    @staticmethod
    def intToKey(n: int):
        return keyboard.KeyCode.from_vk(n)
    
    @staticmethod
    def mouseToStr(button) -> str:
        if button == mouse.Button.left:
            return "l"
        elif button == mouse.Button.middle:
            return "m"
        elif button == mouse.Button.right:
            return "r"
        
    @staticmethod
    def strToMouse(s):
        if s == "l":
            return mouse.Button.left
        elif s == "m":
            return mouse.Button.middle
        elif s == "r":
            return mouse.Button.right  
        
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
    def __on_press(self, key):
        key_code = self.keyToInt(key)
        if not self.__state[self.State.RECORDING] and key_code not in self.__hotkeys[self.Hotkey.START] and key_code not in self.__hotkeys[self.Hotkey.CANCEL]:
            return
        
        if key_code in self.__pressed:
            return

        if self.__state[self.State.RECORDING] and self.InputOption.KEYBOARD in self.__input_option:
            self.__setTime()
            log.info("Pressed {0}".format(key))
            self.__record.append(self.__delay)
            self.__record.append(key_code)
            if key_code in self.__hotkeys[self.Hotkey.STOP]:
                log.debug("Stored hotkey position {0}".format(len(self.__record)-1))
                self.__hotkey_pos_in_record[key_code] = len(self.__record)-1
            
        self.__pressed.add(key_code)
        
        if not self.__state[self.State.RECORDING] and self.__pressed == self.__hotkeys[self.Hotkey.CANCEL]:
            print("[END] Recording has been cancelled")
            return False
            
        if not self.__state[self.State.RECORDING] and self.__pressed == self.__hotkeys[self.Hotkey.START]:
            self.__state[self.State.RECORDING] = True
            self.__pressed.clear()
            self.__prev_mouse_pos = currentMousePosition()
            print("[START] Recording input, press 'ctrl + shift' to end record")
            self.__start = time.time()
        elif self.__state[self.State.RECORDING] and self.__pressed == self.__hotkeys[self.Hotkey.STOP]:
            self.__state[self.State.RECORDING] = False
            self.__removeHotkeyFromRecord()
            print("[END] Recording has finished")
            return False
    
    def __on_release(self, key):
        key_code = self.keyToInt(key)
        if not self.__state[self.State.RECORDING] and key_code not in self.__hotkeys[self.Hotkey.START]:
            return
        
        if key_code not in self.__pressed:
            return

        if self.__state[self.State.RECORDING] and self.InputOption.KEYBOARD in self.__input_option:
            self.__setTime()
            log.info("Released {0}".format(key))
            self.__record.append(self.__delay)
            self.__record.append(key_code)
        
        self.__pressed.remove(key_code)
        
    def __on_press_for_play(self, key):
        key_code = self.keyToInt(key)
        if key_code not in self.__hotkeys[self.Hotkey.START] and key_code not in self.__hotkeys[self.Hotkey.STOP] and key_code not in self.__hotkeys[self.Hotkey.CANCEL]:
            return
        
        if key_code in self.__pressed:
            return
        
        self.__pressed.add(key_code)
        
        if not self.__state[self.State.PLAYING] and self.__pressed == self.__hotkeys[self.Hotkey.CANCEL]:
            print("[END] Playback has been cancelled")
            return False
        
        if not self.__state[self.State.PLAYING] and self.__pressed == self.__hotkeys[self.Hotkey.START]:
            self.__state[self.State.PLAYING] = True
            self.__pressed.clear()
            print("[START] Playing record, press `ctrl + shift` to end playback")
            return False
        elif self.__state[self.State.PLAYING] and self.__pressed == self.__hotkeys[self.Hotkey.STOP]:
            self.__state[self.State.PLAYING] = False
            print("[END] Playback stopped")
            return False
                
    def __on_release_for_play(self, key):
        key_code = self.keyToInt(key)
        
        if key_code not in self.__pressed:
            return
        
        self.__pressed.remove(key_code)
        
    def __show_key(self, key):
        try:
            key_code = key.vk
        except AttributeError:
            key_code = key.value.vk
        print(str(key) + " | " + str(key_code))

    # Mouse listeners
    def __on_move(self, x, y):
        if self.InputOption.MOUSE not in self.__input_option:
            return 
        
        if not self.__state[self.State.RECORDING]:
            return
        
        if self.__mouse_move_counter < 10:
            self.__mouse_move_counter += 1
        else:
            self.__setTime()
            tup = (tuple(self.__prev_mouse_pos), self.__delay, (x, y))
            self.__record.append(tup)
            self.__mouse_move_counter = 0
            self.__prev_mouse_pos = (x, y)
            log.info("Moved mouse to position ({0}, {1})".format(x, y))

    def __on_click(self, x, y, button, pressed):
        if self.InputOption.MOUSE not in self.__input_option:
            return 
        
        if not self.__state[self.State.RECORDING]:
            return
        
        self.__setTime()
        log.info("{0} {1}".format("Pressed" if pressed else "Released", button))
        self.__record.append(self.__delay)
        self.__record.append(self.mouseToStr(button))
            
    def __on_scroll(self, x, y, dx, dy):
        if self.InputOption.MOUSE not in self.__input_option:
            return 
        
        if not self.__state[self.State.RECORDING]:
            return
        
        self.__setTime()
        self.__record.append(self.__delay)
        if dy < 0:
            log.info("Scrolled down")
            self.__record.append("d")
        else:
            log.info("Scrolled up")
            self.__record.append("u")
    
    # Methods
    def record(self, option={InputOption.MOUSE, InputOption.KEYBOARD}):
        if not option:
            return
        
        self.__record.clear()
        self.__input_option = option
        
        print("[READY] Press 'ctrl + shift' to start recording or press 'ctrl + z' to cancel")
        with mouse.Listener(on_move=self.__on_move, on_click=self.__on_click, on_scroll=self.__on_scroll) as listener:
            with keyboard.Listener(on_press=self.__on_press, on_release=self.__on_release) as listener:
                listener.join() 
    
        self.__pressed.clear()
                
    def play(self, loop=1, mouse_movement=MouseMovement.RELATIVE, speed=1.0):
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()
        
        print("[READY] Press 'ctrl + shift' to start playback or press 'ctrl + z' to cancel")
        with keyboard.Listener(on_press=self.__on_press_for_play, on_release=self.__on_release_for_play) as listener:
            listener.join()
        
        if not self.__state[self.State.PLAYING]:
            return
        
        key_listener = keyboard.Listener(on_press=self.__on_press_for_play, on_release=self.__on_release_for_play)
        key_listener.start()
        
        length = len(self.__record)
        i = 0
        loop_count = 0
        while self.__state[self.State.PLAYING] and (loop < 0 or loop_count < loop):
            val = self.__record[i]
            if type(val) is int: # keyboard
                key_code = self.intToKey(val)
                if key_code in self.__pressed:
                    log.info("Releasing " + str(key_code))
                    keyboard_controller.release(key_code)
                    self.__pressed.remove(key_code)
                else:
                    log.info("Pressing " + str(key_code))
                    keyboard_controller.press(key_code)
                    self.__pressed.add(key_code)
            elif type(val) is float: # delay
                time.sleep(self.__speedUp(val, speed))
            elif type(val) is str: # mouse buttons & scroll
                if val == 'l' or val == 'm' or val == 'r':
                    if val in self.__pressed:
                        log.info("Releasing " + val)
                        mouse_controller.release(self.strToMouse(val))
                        self.__pressed.remove(val)
                    else:
                        log.info("Pressing " + val)
                        mouse_controller.press(self.strToMouse(val))
                        self.__pressed.add(val)
                elif val == 'u' or val == 'd':
                    mouse_controller.scroll(0, self.scrollStrToInt(val))
            else: # mouse movement
                if mouse_movement == self.MouseMovement.RELATIVE:
                    current_mouse_pos = tuple(currentMousePosition())
                    rel_x = current_mouse_pos[0] + (val[2][0] - val[0][0])
                    rel_y = current_mouse_pos[1] + (val[2][1] - val[0][1])
                    time.sleep(self.__speedUp(val[1], speed))
                    mouse_controller.position = (rel_x, rel_y)
                    log.info("Moved mouse to position ({0}, {1})".format(rel_x, rel_y))
                else:
                    mouse_controller.position = (val[0][0], val[0][1])
                    time.sleep(self.__speedUp(val[1], speed))
                    mouse_controller.position = (val[2][0], val[2][1])
                    log.info("Moved mouse to position ({0}, {1})".format(val[2][0], val[2][1]))
            i += 1
            if i >= length and (loop < 0 or loop_count < loop):
                i = 0
                loop_count += 1
                
        key_listener.stop()
        if self.__state[self.State.PLAYING] == True:
            self.__state[self.State.PLAYING] = False
            print("[END] Playback finished")
         
        self.__pressed.clear()
        
    def test(self):
        listener = keyboard.Listener(on_press=self.__show_key)
        listener.start()
        try:
            while listener.is_alive():
                time.sleep(1)
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
    if s.endswith(".json"):
        return s
    return s + ".json"

def strToMouseMovement(s: str):
    s = s.lower()
    if s.startswith("abs"):
        return Input.MouseMovement.ABSOLUTE
    elif s.startswith("rel"):
        return Input.MouseMovement.RELATIVE

def addRecord(args, record_dir):
    record_dir = Path(record_dir)
    if not record_dir.exists():
        record_dir.mkdir(parents=True)
        
    input = Input()
    input_option = set()
    record_name = strToJson(args.record)
    if args.mouse:
        input_option.add(Input.InputOption.MOUSE)
    if args.keyboard:
        input_option.add(Input.InputOption.KEYBOARD)
    
    if not input_option:
        print("[ERROR] Input option cannot be empty, try adding either '-m' or '-k' flag")
        return
    
    input.record(option=input_option)
    if not input.isRecordEmpty():
        input.saveRecordToJson(record_dir.joinpath(record_name))
    
def removeRecord(args, record_dir):
    record_dir = Path(record_dir)
    files = args.record
    for i in files:  
        file = record_dir.joinpath(strToJson(i))
        if file.exists():
            file.unlink()
            print("[SUCCESS] Deleted record {0}".format(file.stem))
    
def listRecords(path):
    path = Path(path)
    if not path.exists():
        print("[ERROR] Record directory does not exist")
        return
        
    print("Records:")
    files = path.glob('*')
    for file in files:
        print("  " + file.stem)
        
def playRecord(args, record_dir):
    record_dir = Path(record_dir)
    input = Input()
    record_name = str(record_dir.joinpath(strToJson(args.record)))
    input.getRecordFromJson(record_name)
    input.play(args.loop, strToMouseMovement(args.movement), args.speed)
    
def readConfig(config_path) -> dict:
    with open(config_path, 'r') as file:
        data = json.load(file)
    return data

def writeConfig(config, config_path):
    data = json.dumps(config, indent=4)
    with open(config_path, 'w') as file:
        file.write(data)

def main():
    current_dir = Path(__file__).parent.resolve()
    config_path = current_dir.joinpath("config.json")
    config = {"recordDirectory" : str(current_dir.joinpath("records"))}

    # input = Input()
    # input.test()
    
    if not config_path.exists():
        writeConfig(config, config_path)
    else:
        config = readConfig(config_path)
        
    record_dir = config["recordDirectory"]
    
    # main
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version="%(prog)s {0}".format("0.1.1-alpha"))
    subparser = parser.add_subparsers(dest="command1")
    
    # record
    cmd_record = subparser.add_parser("record", help="record input")
    record_subparser = cmd_record.add_subparsers(dest="command2")
    
    # record add
    cmd_record_add = record_subparser.add_parser("add", help="add a new record")
    cmd_record_add.add_argument("record", type=str)
    cmd_record_add.add_argument("-m", "--mouse", action="store_true", dest="mouse", help="enable mouse when recording")
    cmd_record_add.add_argument("-k", "--keyboard", action="store_true", dest="keyboard", help="enable keyboard when recording")
    
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
    cmd_play.add_argument("-m", "--movement", nargs='?', type=str, default="rel", dest="movement", help="the type of mouse movement to use (absolute or relative)")
    
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
            addRecord(args, record_dir)
        elif args.command2 == "remove":
            removeRecord(args, record_dir)
        elif args.command2 == "list":
            listRecords(record_dir)
    elif args.command1 == "play":
        if args.all:
            listRecords(record_dir)
            exit()
        playRecord(args, record_dir)
    elif args.command1 == "config":
        if args.command2 == "set":
            key = args.config[0]
            val = args.config[1]
            if key in config:
                config[key] = val
                writeConfig(config, config_path)
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
    
# keyboard = int
# time = float
# scroll = str(u | d)
# mouse movement = tuple(3)
# mouse button = str(l | m | r)