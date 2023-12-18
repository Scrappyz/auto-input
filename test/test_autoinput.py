import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

from autoinput import *

class TestAutoInput(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(Hotkey.parse("ctrl_l+shift_r"), [keyboard.Key.ctrl_l, keyboard.Key.shift_r])
        self.assertEqual(Hotkey.parse("ctrl_l + shift_r"), [keyboard.Key.ctrl_l, keyboard.Key.shift_r])
        self.assertEqual(Hotkey.parse("ctrl_l+z"), [keyboard.Key.ctrl_l, keyboard.KeyCode.from_char('z')])
        
    def test_hotkeyToCode(self):
        self.assertEqual(Hotkey.hotkeyToCode(keyboard.Key.ctrl_l), 162)
        
    def test_hotkeyToCombo(self):
        self.assertEqual(Hotkey.hotkeyToCombo("ctrl_l+shift_r"), {keyboard.Key.ctrl_l, keyboard.Key.shift_r})
        self.assertEqual(Hotkey.hotkeyToCombo("ctrl_l + shift_r"), {keyboard.Key.ctrl_l, keyboard.Key.shift_r})
        self.assertEqual(Hotkey.hotkeyToCombo("ctrl_l+z"), {keyboard.Key.ctrl_l, keyboard.KeyCode.from_char('z')})
        self.assertEqual(Hotkey.hotkeyToCombo([keyboard.Key.ctrl_l, keyboard.Key.shift_r]), {keyboard.Key.ctrl_l, keyboard.Key.shift_r})
        
    def test_strToJson(self):
        self.assertEqual(strToJson("wassup"), "wassup.json")
        self.assertEqual(strToJson("wassup.json"), "wassup.json")
        
if __name__ == "__main__":
    unittest.main()