from pynput.keyboard import Listener  as KeyboardListener
from pynput.mouse    import Listener  as MouseListener
from pynput.keyboard import Key
import time

input = []
key = ""
start = 0
end = 0
prev = 0

def printInput():
    global input
    for i in range(len(input)):
        print(i)

def end_rec(key):
    print(str(key))

def on_press(key):
    global prev, end
    print(str(key))
    end = time.time()
    print(end - start - prev)
    prev = end - start
    if key == Key.ctrl_r:
        return False

def on_move(x, y):
    print("Mouse moved to ({0}, {1})".format(x, y))

def on_click(x, y, button, pressed):
    if pressed:
        print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))

def on_scroll(x, y, dx, dy):
    print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))


with MouseListener(on_click=on_click, on_scroll=on_scroll) as listener:
    with KeyboardListener(on_press=on_press) as listener:
        start = time.time()
        listener.join()
        