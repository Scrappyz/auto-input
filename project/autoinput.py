import time
import logging
import pyautogui
import json
from pathlib import Path
from pynput import mouse
from pynput import keyboard

logging.basicConfig(format="%(message)s")
log = logging.getLogger()
log.setLevel(logging.INFO)

class Input:
    __record = []
    __pressed = set()
    __prev_mouse_pos = (-1, -1)
    __mouse_move_counter = 0
    __start = 0
    __end = 0
    __delay = 0
    
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
    
    # Helper
    def __setTime(self):
        self.__end = time.time()
        current = self.__end - self.__start
        self.__delay = float(int((current) * 1000) / 1000)
        self.__start = time.time()
        
    def keyToInt(self, key) -> int:
        try:
            key_code = key.vk
        except AttributeError:
            key_code = key.value.vk
        return key_code
    
    def intToKey(self, n: int):
        return keyboard.KeyCode.from_vk(n)
    
    # Keyboard listeners
    def on_press(self, key):
        if key == keyboard.Key.shift_r:
            return False
        if key in self.__pressed:
            return
        self.__setTime()
        log.info(str(key) + " is pressed")
        self.__record.append(self.__delay)
        self.__record.append(self.keyToInt(key))
        self.__pressed.add(key)
    
    def on_release(self, key):
        self.__setTime()
        log.info(str(key) + " is released")
        self.__record.append(self.__delay)
        self.__record.append(self.keyToInt(key))
        self.__pressed.remove(key)

    # Mouse listeners
    def on_move(self, x, y):
        if self.__mouse_move_counter < 10:
            self.__mouse_move_counter += 1
        else:
            self.__setTime()
            tup = (tuple(self.__prev_mouse_pos), self.__delay, (x, y))
            self.__record.append(tup)
            self.__mouse_move_counter = 0
            self.__prev_mouse_pos = (x, y)
            log.info(str(x) + " | " + str(y))
            log.info(str(self.__delay))

    def on_click(self, x, y, button, pressed):
        self.__setTime()
        log.info("{0} is {1}".format(button, "pressed" if pressed else "released"))
        self.__record.append(self.__delay)
        if button == mouse.Button.left:
            self.__record.append("l")
        elif button == mouse.Button.middle:
            self.__record.append("m")
        elif button == mouse.Button.right:
            self.__record.append("r")
            
    def on_scroll(self, x, y, dx, dy):
        self.__setTime()
        self.__record.append(self.__delay)
        if dy < 0:
            log.info("Scrolled down: " + str(dx) + " | " + str(dy))
            self.__record.append("d")
        else:
            log.info("Scrolled up: " + str(dx) + " | " + str(dy))
            self.__record.append("u")
    
    # Methods
    def record(self):
        self.__record.clear()
        self.__prev_mouse_pos = pyautogui.position()
        with mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as listener:
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                self.__start = time.time()
                self.__prev = self.__start
                listener.join() 
        self.__pressed.clear()
                
    def play(self, loop=False):
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
                        mouse_controller.release(mouse.Button.left)
                        self.__pressed.remove(val)
                    else:
                        log.info("Pressing " + val)
                        mouse_controller.press(mouse.Button.left)
                        self.__pressed.add(val)
                elif val == 'u' or val == 'd':
                    if val == 'u':
                        mouse_controller.scroll(0, 1)
                    else:
                        mouse_controller.scroll(0, -1)
            else:
                mouse.Controller().position = (val[0][0], val[0][1])
                time.sleep(val[1])
                mouse.Controller().position = (val[2][0], val[2][1])
            i += 1
            if i == length and loop:
                i = 0
        self.__pressed.clear()
                
    def printInput(self):
        for i in range(len(self.__record)):
            print(self.__record[i])
        print("Length: {0}".format(len(self.__record)))
            
    def printTypes(self):
        for i in self.__record:
            print(type(i))

def main():
    current_path = Path(__file__).parent.resolve()
    input = Input()
    input.getRecordFromJson(Path.joinpath(current_path, "test.json"))
    time.sleep(2)
    input.play(loop=True)
    
if __name__ == "__main__":
    main()
    
# keyboard = int
# time = float
# scroll = str(u | d)
# mouse movement = tuple(3)
# mouse button = str(l | m | r)