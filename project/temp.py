import threading
import time

def print_numbers1():
    for i in range(1, 6):
        print(f"Function 1: {i}")
        time.sleep(0)

def print_numbers2():
    for i in range(7, 12):
        print(f"Function 2: {i}")
        time.sleep(0)

thread1 = threading.Thread(target=print_numbers1)
thread2 = threading.Thread(target=print_numbers2)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
