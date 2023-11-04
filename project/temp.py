from time import sleep
from pynput import keyboard

def on_press(key):
    try:
        key_code = key.vk
    except AttributeError:
        key_code = key.value.vk
    print(key_code)

listener = keyboard.Listener(on_press=on_press)
listener.start()
try:
    while listener.is_alive():
        sleep(1)
except KeyboardInterrupt:
    listener.stop()