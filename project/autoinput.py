import time
import logging
import json
import sys
from enum import Enum
from pyautogui import position as currentMousePosition
from pathlib import Path
from pynput import mouse
from pynput import keyboard

logging.basicConfig(format="[%(levelname)s] %(message)s")
log = logging.getLogger()
log.setLevel(logging.DEBUG)

class Input:
    class RecordOption(Enum):
        MOUSE = 1
        KEYBOARD = 2
        MOUSE_AND_KEYBOARD = 3
        
    class MouseMovement(Enum):
        ABSOLUTE = 1
        RELATIVE = 2
    
    def __init__(self):
        self.__record = []
        self.__recording = False
        self.__hotkey = {162, 160} # ctrl + shift
        self.__cancel_hotkey = {162, 90} # ctrl + z
        self.__record_option = self.RecordOption.MOUSE_AND_KEYBOARD
        
        # Helper variables
        self.__pressed = set()
        self.__prev_mouse_pos = (-1, -1)
        self.__mouse_move_counter = 0
        self.__start = 0
        self.__end = 0
        self.__delay = 0
        self.__hotkey_pos_in_record = {}
        for i in self.__hotkey:
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
        if self.__record_option == self.RecordOption.MOUSE: # do not pop if keyboard not included
            return
        
        self.__pressed.clear()
        self.printInput()
        
        # 0 1 2 3 4
        # 1 2 3 4 5
        
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
        
    def __setKeysEqualToDictKeys(set: set, dict: dict) -> bool:
        dict_keys = dict.keys()
        if len(set) != len(dict_keys):
            return False
        
        for i, j in zip(set, dict):
            if i != j:
                return False
        
        return True
            
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
    
    # Keyboard listeners
    def __on_press(self, key):
        key_code = self.keyToInt(key)
        if not self.__recording and key_code not in self.__hotkey and key_code not in self.__cancel_hotkey:
            return
        
        if key_code in self.__pressed:
            return

        if self.__recording and self.__record_option != self.RecordOption.MOUSE:
            self.__setTime()
            log.info("Pressed {0}".format(key))
            self.__record.append(self.__delay)
            self.__record.append(key_code)
            if key_code in self.__hotkey:
                log.debug("Stored hotkey position {0}".format(len(self.__record)-1))
                self.__hotkey_pos_in_record[key_code] = len(self.__record)-1
            
        self.__pressed.add(key_code)
        
        if not self.__recording and self.__cancel_hotkey.issubset(self.__pressed):
            print("[END] Recording has been cancelled")
            return False
        
        if self.__pressed == self.__hotkey:
            if not self.__recording:
                self.__recording = True
                self.__pressed.clear()
                self.__prev_mouse_pos = currentMousePosition()
                print("[START] Recording input, press 'ctrl + shift' to end record")
            else:
                self.__recording = False
                self.__removeHotkeyFromRecord()
                print("[END] Recording has finished")
                return False
    
    def __on_release(self, key):
        key_code = self.keyToInt(key)
        if not self.__recording and key_code not in self.__hotkey:
            return
        
        if key_code not in self.__pressed:
            return

        if self.__recording and self.__record_option != self.RecordOption.MOUSE:
            self.__setTime()
            log.info("Released {0}".format(key))
            self.__record.append(self.__delay)
            self.__record.append(key_code)
        
        self.__pressed.remove(key_code)
        
    def __show_key(self, key):
        try:
            key_code = key.vk
        except AttributeError:
            key_code = key.value.vk
        print(str(key) + " | " + str(key_code))

    # Mouse listeners
    def __on_move(self, x, y):
        if self.__record_option == self.RecordOption.KEYBOARD:
            return 
        
        if not self.__recording:
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
        if self.__record_option == self.RecordOption.KEYBOARD:
            return 
        
        if not self.__recording:
            return
        
        self.__setTime()
        log.info("{0} {1}".format("Pressed" if pressed else "Released", button))
        self.__record.append(self.__delay)
        self.__record.append(self.mouseToStr(button))
            
    def __on_scroll(self, x, y, dx, dy):
        if self.__record_option == self.RecordOption.KEYBOARD:
            return 
        
        if not self.__recording:
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
    def record(self, option=RecordOption.MOUSE_AND_KEYBOARD):
        self.__record.clear()
        self.__record_option = option
        
        print("[READY] Press 'ctrl + shift' to start recording or press 'ctrl + z' to cancel")
        with mouse.Listener(on_move=self.__on_move, on_click=self.__on_click, on_scroll=self.__on_scroll) as listener:
            with keyboard.Listener(on_press=self.__on_press, on_release=self.__on_release) as listener:
                self.__start = time.time()
                listener.join() 
    
        self.__pressed.clear()
                
    def play(self, loop=False, mouse_movement=MouseMovement.ABSOLUTE):
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()
        length = len(self.__record)
        i = 0
        while i < length or loop:
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
                time.sleep(val)
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
                    time.sleep(val[1])
                    mouse_controller.position = (rel_x, rel_y)
                else:
                    mouse_controller.position = (val[0][0], val[0][1])
                    time.sleep(val[1])
                    mouse_controller.position = (val[2][0], val[2][1])
            i += 1
            if i == length and loop:
                i = 0
        self.__pressed.clear()
        
    def test(self):
        listener = keyboard.Listener(on_press=self.__show_key)
        listener.start()
        try:
            while listener.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            listener.stop()
                
    def printInput(self):
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

def main():
    current_path = Path(__file__).parent.resolve()
    record_path = Path.joinpath(current_path).parent.joinpath("records")
    input = Input()
    
    input.record(option=Input.RecordOption.MOUSE_AND_KEYBOARD)
    print(sys.getsizeof(input.getRecord()))
    # # input.test()

    print("===========")
    input.printInput()
    print("==========")

    # input.play(mouse_movement=Input.MouseMovement.RELATIVE)
    
    # time.sleep(2)
    # input.record()
    # input.saveRecordToJson(Path.joinpath(record_path, "test.json"))
    
    # input.getRecordFromJson(Path.joinpath(record_path, "test.json"))
    # time.sleep(2)
    # input.play(loop=True)
    
if __name__ == "__main__":
    main()
    
# keyboard = int
# time = float
# scroll = str(u | d)
# mouse movement = tuple(3)
# mouse button = str(l | m | r)