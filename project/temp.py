import time
from pynput import keyboard

run = True

def on_press(key):
    global run
    try:
        key_code = key.vk
    except AttributeError:
        key_code = key.value.vk
    if key == keyboard.Key.shift_r:
        run = False
    print(key_code)

def main():
    k = keyboard.Listener(on_press=on_press)
    k.start()
    while run:
        print("Running")
        time.sleep(1)
    k.stop()
    
if __name__ == "__main__":
    main()