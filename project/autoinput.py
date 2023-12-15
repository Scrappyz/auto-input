import mouse, keyboard
import json
import time

class Recorder:
    def __init__(self) -> None:
        self.__record = []
        
    def __mouseInput(self, event):
        self.__record.append(event)
        
    def __keyboardInput(self, event):
        self.__record.append(event)
        
    def record(self):
        mouse.hook(self.__mouseInput)
        keyboard.hook(self.__keyboardInput)
        
        keyboard.wait("ctrl + shift")
        
        mouse.unhook_all()
        keyboard.unhook_all()
           
def _test():
    print("wassup")

def main():
    record()
    
if __name__ == "__main__":
    main()
    
# Notes
# use lists with IntEnum rather than dict in record