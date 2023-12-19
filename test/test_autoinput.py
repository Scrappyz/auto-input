import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

from autoinput import *

class TestAutoInput(unittest.TestCase):
    def test_getHotkeyName(self):
        hotkey = Hotkey("ctrl+shift")
        self.assertEqual(hotkey.getHotkeyName(), "ctrl + shift")
    
    def test_parse(self):
        self.assertEqual(Hotkey.parse("ctrl+shift_r"), ["ctrl", "shift_r"])
        self.assertEqual(Hotkey.parse("ctrl + shift_r"), ["ctrl", "shift_r"])
        self.assertEqual(Hotkey.parse("ctrl+z"), ["ctrl", "z"])
        
    def test_keyToCode(self):
        self.assertEqual(Hotkey.keyToCode("ctrl"), 162)
        self.assertEqual(Hotkey.keyToCode("ctrl", True), [162])
        self.assertEqual(Hotkey.keyToCode("ctrl + shift"), [162, 160])
        self.assertEqual(Hotkey.keyToCode("ctrl + a"), [162, 65])
        
    def test_keyToCombo(self):
        self.assertEqual(Hotkey.keyToCombo("ctrl+shift"), {162, 160})
        self.assertEqual(Hotkey.keyToCombo("ctrl + shift"), {162, 160})
        self.assertEqual(Hotkey.keyToCombo("ctrl+a"), {162, 65})
        self.assertEqual(Hotkey.keyToCombo([162, 65]), {162, 65})
        
    def test_isKey(self):
        # self.assertEqual(Hotkey.isKey(keyboard.Key.shift_r), True)
        # self.assertEqual(Hotkey.isKey(keyboard.KeyCode.from_vk(65)), True)
        self.assertEqual(Hotkey.isKey("ctrl"), True)
        self.assertEqual(Hotkey.isKey("a"), True)
        self.assertEqual(Hotkey.isKey(65), True)
        self.assertEqual(Hotkey.isKey("cteg"), False)
        
    def test_addToPressedKeys(self):
        Hotkey.addToPressedKeys("a")
        self.assertEqual(Hotkey.getPressedKeys(), {65})
        Hotkey.addToPressedKeys("ctrl")
        self.assertEqual(Hotkey.getPressedKeys(), {65, 162})
        Hotkey.addToPressedKeys(62)
        self.assertEqual(Hotkey.getPressedKeys(), {65, 162, 62})
        Hotkey.addToPressedKeys('a')
        self.assertEqual(Hotkey.getPressedKeys(), {65, 162, 62})
        Hotkey.releaseAllKeys()
        self.assertEqual(Hotkey.getPressedKeys(), set())
        
    # def test_strToJson(self):
    #     self.assertEqual(strToJson("wassup"), "wassup.json")
    #     self.assertEqual(strToJson("wassup.json"), "wassup.json")
        
if __name__ == "__main__":
    unittest.main()