import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

from autoinput import *
from pynput import mouse, keyboard

class TestAutoInput(unittest.TestCase):
    def test_hotkey(self):
        hotkey = Hotkey("ctrl+shift")
        self.assertEqual(hotkey.getHotkeyName(), "ctrl + shift")
        self.assertEqual(hotkey.getHotkey(), ["ctrl", "shift"])
        self.assertEqual(hotkey.getHotkeyCombo(), {"ctrl", "shift"})
        
        h = Hotkey(hotkey)
        self.assertEqual(h.getHotkeyName(), "ctrl + shift")
        self.assertEqual(h.getHotkey(), ["ctrl", "shift"])
        self.assertEqual(h.getHotkeyCombo(), {"ctrl", "shift"})
    
    def test_parse(self):
        self.assertEqual(Hotkey.parse("ctrl+shift_r"), ["ctrl", "shift_r"])
        self.assertEqual(Hotkey.parse("ctrl + shift_r"), ["ctrl", "shift_r"])
        self.assertEqual(Hotkey.parse("ctrl+z"), ["ctrl", "z"])
        
    def test_toString(self):
        self.assertEqual(toString(162), "ctrl")
        self.assertEqual(toString([162, 160]), "ctrl + shift")
        self.assertEqual(toString([keyboard.KeyCode.from_vk(162), keyboard.KeyCode.from_vk(160)]), "ctrl + shift")
        self.assertEqual(toString([keyboard.KeyCode.from_vk(162), keyboard.KeyCode.from_char('a')]), "ctrl + a")
        self.assertEqual(toString(mouse.Button.left), "LMB")
        self.assertEqual(toString(mouse.Button.right), "RMB")
        
    def test_toKeyCode(self):
        self.assertEqual(toKeyCode("ctrl"), 162)
        self.assertEqual(toKeyCode("ctrl", True), [162])
        self.assertEqual(toKeyCode("ctrl + shift"), [162, 160])
        self.assertEqual(toKeyCode("ctrl + a"), [162, 65])
        self.assertEqual(toKeyCode([162,65]), [162, 65])
        self.assertEqual(toKeyCode(["ctrl", "a"]), [162, 65])
        self.assertEqual(toKeyCode(keyboard.KeyCode.from_vk(162)), 162)
        self.assertEqual(toKeyCode([keyboard.KeyCode.from_vk(162), keyboard.KeyCode.from_char('a')]), [162, 65])
        
    def test_toCombo(self):
        self.assertEqual(toCombo("ctrl+shift"), {"ctrl", "shift"})
        self.assertEqual(toCombo("ctrl + shift"), {"ctrl", "shift"})
        self.assertEqual(toCombo("ctrl+a"), {"ctrl", "a"})
        self.assertEqual(toCombo([162, 65]), {"ctrl", "a"})
        
    def test_toKey(self):
        self.assertEqual(toKey("ctrl"), keyboard.KeyCode.from_vk(162))
        self.assertEqual(toKey("ctrl", True), [keyboard.KeyCode.from_vk(162)])
        self.assertEqual(toKey("ctrl+shift"), [keyboard.KeyCode.from_vk(162), keyboard.KeyCode.from_vk(160)])
        self.assertEqual(toKey([162, 160]), [keyboard.KeyCode.from_vk(162), keyboard.KeyCode.from_vk(160)])
        self.assertEqual(toKey([keyboard.KeyCode.from_vk(162), keyboard.KeyCode.from_vk(160)]), [keyboard.KeyCode.from_vk(162), keyboard.KeyCode.from_vk(160)])
        
    def test_toButton(self):
        self.assertEqual(toButton("LMB"), mouse.Button.left)
        self.assertEqual(toButton("RMB"), mouse.Button.right)
        
    def test_isKey(self):
        self.assertEqual(isKey(keyboard.Key.shift_r), True)
        self.assertEqual(isKey(keyboard.KeyCode.from_vk(65)), True)
        self.assertEqual(isKey(keyboard.KeyCode.from_vk(165)), True)
        
    # def test_strToJson(self):
    #     self.assertEqual(strToJson("wassup"), "wassup.json")
    #     self.assertEqual(strToJson("wassup.json"), "wassup.json")
        
if __name__ == "__main__":
    unittest.main()