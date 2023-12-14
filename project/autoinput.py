import mouse, keyboard
import json
import threading
import time

# def recordInput():
#     keyboard_input = threading.Thread(target=keyboard.record, args=("ctrl + shift"))
#     mouse_input = threading.Thread(target=mouse.record, args=("ctrl + shift"))
    
#     keyboard_input.start()
#     mouse_input.start()
    
#     keyboard_input.join()
#     mouse_input.join()
    
class Input:
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
        
    def printRecord(self):
        for i in self.__record:
            print(type(i))

def main():
    input = Input()
    input.record()
    input.printRecord()
    
if __name__ == "__main__":
    main()