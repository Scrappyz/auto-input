import time
import logging
from pynput import mouse
from pynput import keyboard
from pyautogui import moveTo, moveRel

logging.basicConfig(format="%(message)s")
log = logging.getLogger()
log.setLevel(logging.INFO)

class Input:
    __input = []
    __pressed = set()
    __start = 0
    __prev = 0
    __end = 0
    __delay = 0
    
    # Helper
    def __setTime(self):
        self.__end = time.time()
        current = self.__end - self.__start
        self.__delay = float(int((current - self.__prev) * 1000) / 1000)
        self.__prev = current
    
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
        log.info("Mouse moved to ({0}, {1})".format(x, y))
        self.__setTime()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.__setTime()
            log.info(str(button) + " is pressed")
            self.__input.append(self.__delay)
            self.__input.append(button)
        else:
            self.__setTime()
            log.info(str(button) + " is released")
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
        with mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll) as listener:
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                self.__start = time.time()
                listener.join() 
        self.__pressed.clear()
                
    def play(self):
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()
        for i in range(len(self.__input)):
            if type(self.__input[i]) is float:
                time.sleep(self.__input[i])
                # i += 1
            elif type(self.__input[i]) is int:
                log.info("Scrolled {0}".format("down" if self.__input[i] < 0 else "up"))
                mouse_controller.scroll(0, self.__input[i])
            else:
                if type(self.__input[i]) is keyboard._win32.KeyCode or type(self.__input[i]) is keyboard.Key:
                    if self.__input[i] in self.__pressed:
                        log.info("Releasing " + str(self.__input[i]))
                        keyboard_controller.release(self.__input[i])
                        self.__pressed.remove(self.__input[i])
                    else:
                        log.info("Pressing " + str(self.__input[i]))
                        keyboard_controller.press(self.__input[i])
                        self.__pressed.add(self.__input[i])
                elif type(self.__input[i]) is mouse.Button:
                    if self.__input[i] in self.__pressed:
                        log.info("Releasing " + str(self.__input[i]))
                        mouse_controller.release(self.__input[i])
                        self.__pressed.remove(self.__input[i])
                    else:
                        log.info("Pressing " + str(self.__input[i]))
                        mouse_controller.press(self.__input[i])
                        self.__pressed.add(self.__input[i])
        self.__pressed.clear()
                
    def printInput(self):
        for i in range(len(self.__input)):
            print(self.__input[i])
            
    def printTypes(self):
        for i in self.__input:
            print(type(i))

def main():
    input = Input()
    input.record()
    print("===========")
    input.printInput()
    print("===========")
    
    time.sleep(3)
    input.play()
    
if __name__ == "__main__":
    main()