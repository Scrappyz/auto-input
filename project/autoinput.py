import time
import logging
import pyautogui
import json
from pynput import mouse
from pynput import keyboard

logging.basicConfig(format="%(message)s")
log = logging.getLogger()
log.setLevel(logging.INFO)

class Input:
    __input = []
    __pressed = set()
    __prev_mouse_pos = (-1, -1)
    __mouse_move_counter = 0
    __start = 0
    __end = 0
    __delay = 0
    
    # Helper
    def __setTime(self):
        self.__end = time.time()
        current = self.__end - self.__start
        self.__delay = float(int((current) * 1000) / 1000)
        self.__start = time.time()
    
    # Keyboard listeners
    def on_press(self, key):
        if key == keyboard.Key.shift_r:
            return False
        if key in self.__pressed:
            return
        self.__setTime()
        log.info(str(key) + " is pressed")
        self.__input.append(self.__delay)
        self.__input.append(key)
        self.__pressed.add(key)
    
    def on_release(self, key):
        self.__setTime()
        log.info(str(key) + " is released")
        self.__input.append(self.__delay)
        self.__input.append(key)
        self.__pressed.remove(key)

    # Mouse listeners
    def on_move(self, x, y):
        
        if self.__mouse_move_counter < 10:
            self.__mouse_move_counter += 1
        else:
            self.__setTime()
            tup = (tuple(self.__prev_mouse_pos), self.__delay, (x, y))
            self.__input.append(tup)
            self.__mouse_move_counter = 0
            self.__prev_mouse_pos = (x, y)
            log.info(str(x) + " | " + str(y))
            log.info(str(self.__delay))

    def on_click(self, x, y, button, pressed):
        self.__setTime()
        log.info("{0} is {1}".format(button, "pressed" if pressed else "released"))
        self.__input.append(self.__delay)
        self.__input.append(button)
            
    def on_scroll(self, x, y, dx, dy):
        self.__setTime()
        self.__input.append(self.__delay)
        self.__input.append(dy)
        if dy < 0:
            log.info("Scrolled down: " + str(dx) + " | " + str(dy))
        else:
            log.info("Scrolled up: " + str(dx) + " | " + str(dy))
    
    # Methods
    def record(self):
        self.__input.clear()
        self.__prev_mouse_pos = pyautogui.position()
        with mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as listener:
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                self.__start = time.time()
                self.__prev = self.__start
                listener.join() 
        self.__pressed.clear()
                
    def play(self):
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()
        for i in range(len(self.__input)):
            val = self.__input[i]
            if type(val) is float:
                time.sleep(val)
            elif type(val) is int:
                log.info("Scrolled {0}".format("down" if val < 0 else "up"))
                mouse_controller.scroll(0, val)
            else:
                if type(val) is keyboard._win32.KeyCode or type(val) is keyboard.Key:
                    if val in self.__pressed:
                        log.info("Releasing " + str(val))
                        keyboard_controller.release(val)
                        self.__pressed.remove(val)
                    else:
                        log.info("Pressing " + str(val))
                        keyboard_controller.press(val)
                        self.__pressed.add(val)
                elif type(val) is mouse.Button:
                    if val in self.__pressed:
                        log.info("Releasing " + str(val))
                        mouse_controller.release(val)
                        self.__pressed.remove(val)
                    else:
                        log.info("Pressing " + str(val))
                        mouse_controller.press(val)
                        self.__pressed.add(val)
                else:
                    # pyautogui.moveTo(val[0][0], val[0][1])
                    # pyautogui.moveTo(val[2][0], val[2][1], val[1])
                    mouse.Controller().position = (val[0][0], val[0][1])
                    time.sleep(val[1])
                    mouse.Controller().position = (val[2][0], val[2][1])
        self.__pressed.clear()
                
    def printInput(self):
        for i in range(len(self.__input)):
            print(self.__input[i])
        print("Length: {0}".format(len(self.__input)))
            
    def printTypes(self):
        for i in self.__input:
            print(type(i))
            
def testSpeed(t: float):
    i = 0
    while True:
        print(i)
        i += 1
        time.sleep(t)

def main():
    input = Input()
    input.record()
    print("===========")
    input.printInput()
    print("===========")
    
    time.sleep(3)
    input.play()
    
    # testSpeed(0.010)
    
if __name__ == "__main__":
    main()