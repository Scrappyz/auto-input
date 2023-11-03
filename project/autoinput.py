import time
from pynput import mouse
from pynput import keyboard

class Input:
    __input = []
    __pressed = set()
    __start = 0
    __prev = 0
    __end = 0
    __delay = 0
    
    def __setTime(self):
        self.__end = time.time()
        current = self.__end - self.__start
        self.__delay = int((current - self.__prev) * 1000) / 1000
        self.__prev = current
    
    def on_press(self, key):
        if key in self.__pressed:
            return
        self.__setTime()
        self.__input.append(self.__delay)
        self.__input.append(key)
        print(str(key) + " is pressed")
        self.__pressed.add(key)
    
    def on_release(self, key):
        self.__setTime()
        self.__input.append(self.__delay)
        self.__input.append(key)
        print(str(key) + " is released")
        self.__pressed.remove(key)
        if key == keyboard.Key.shift_r:
            return False

    def on_move(self, x, y):
        print("Mouse moved to ({0}, {1})".format(x, y))
        self.__setTime()

    def on_click(self, x, y, button, pressed):
        if pressed:
            print(str(button) + " is pressed")
            self.__setTime()
            self.__input.append(self.__delay)
            self.__input.append(button)
        else:
            print(str(button) + " is released")
            self.__setTime()
            self.__input.append(self.__delay)
            self.__input.append(button)
            
    def record(self):
        self.__input.clear()
        with mouse.Listener(on_click=self.on_click) as listener:
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                self.__start = time.time()
                listener.join() 
        self.__pressed.clear()
                
    def play(self):
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()
        for i in self.__input:
            if type(i) is int:
                time.sleep(i)
            else:
                if type(i) is keyboard._win32.KeyCode or type(i) is keyboard.Key:
                    keyboard_controller.press(i)
                elif type(i) is mouse.Button:
                    mouse_controller.click(i)
                
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

    # time.sleep(3)
    # input.play()

if __name__ == "__main__":
    main()