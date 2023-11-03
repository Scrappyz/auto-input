import time
# from pynput.keyboard import Listener  as KeyboardListener
# from pynput.mouse    import Listener  as MouseListener
# from pynput.keyboard import Key
# from pynput.mouse import Button
# from pynput.keyboard import Controller as KeyboardController
# from pynput.mouse import Controller as MouseController
# from pynput.keyboard._win32.
from pynput import mouse
from pynput import keyboard

class Input:
    __input = []
    __start = 0
    __prev = 0
    __end = 0
    __delay = 0
    
    def __setTime(self):
        self.__end = time.time()
        current = self.__end - self.__start
        self.__delay = current - self.__prev
        self.__prev = current
    
    def on_press(self, key):
        self.__setTime()
        self.__input.append(self.__delay)
        self.__input.append(key)
        if key == keyboard.Key.shift_r:
            return False

    def on_move(self, x, y):
        print("Mouse moved to ({0}, {1})".format(x, y))
        self.__setTime()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.__setTime()
            self.__input.append(self.__delay)
            self.__input.append(button)
            
    def record(self):
        self.__input.clear()
        with mouse.Listener(on_click=self.on_click) as listener:
            with keyboard.Listener(on_press=self.on_press) as listener:
                self.__start = time.time()
                listener.join() 
                
    def play(self):
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()
        time.sleep(3)
        for i in self.__input:
            if type(i) is float:
                time.sleep(i)
                print(i)
            else:
                if type(i) is keyboard._win32.KeyCode or type(i) is keyboard.Key:
                    keyboard_controller.press(i)
                elif type(i) is mouse.Button:
                    mouse_controller.press(i)
                
    def printInput(self):
        for i in range(len(self.__input)):
            print(self.__input[i])
            
    def printTypes(self):
        for i in self.__input:
            print(type(i))

def main():
    input = Input()
    input.record()
    input.printInput()

if __name__ == "__main__":
    main()