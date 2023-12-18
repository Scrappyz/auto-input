import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

from autoinput import *

class TestAutoInput(unittest.TestCase):
    def test_getHotkeyName(self):
        hotkey = Hotkey("ctrl + right shift + a")
        self.assertEqual(hotkey.getHotkeyName(), "ctrl + right shift + a")
            
    def test_splitKeys(self):
        self.assertEqual(Hotkey.splitKeys("shift"), ["shift"])
        self.assertEqual(Hotkey.splitKeys("ctrl+shift"), ["ctrl", "shift"])
        self.assertEqual(Hotkey.splitKeys("ctrl + shift"), ["ctrl", "shift"])
        self.assertEqual(Hotkey.splitKeys("ctrl   +   shift  "), ["ctrl", "shift"])
        self.assertEqual(Hotkey.splitKeys("ctrl + right shift"), ["ctrl", "right shift"])
        self.assertEqual(Hotkey.splitKeys("right ctrl + right shift"), ["right ctrl", "right shift"])
        self.assertEqual(Hotkey.splitKeys("right + right shift"), ["right", "right shift"])
        self.assertEqual(Hotkey.splitKeys("left + right shift"), ["left", "right shift"])
        self.assertEqual(Hotkey.splitKeys("left + right + middle"), ["left", "right", "middle"])
        
    def test_hotkeyToCode(self):
        self.assertEqual(Hotkey.hotkeyToCode("ctrl + shift"), [29, 42])
        self.assertEqual(Hotkey.hotkeyToCode("ctrl"), 29)
        self.assertEqual(Hotkey.hotkeyToCode([29, 42]), [29, 42])
        self.assertEqual(Hotkey.hotkeyToCode(Hotkey("ctrl + shift")), [29, 42])
        self.assertEqual(Hotkey.hotkeyToCode(Hotkey("ctrl")), 29)
        self.assertEqual(Hotkey.hotkeyToCode(Hotkey("ctrl"), True), [29])
        
    def test_hotkeyToCombo(self):
        self.assertEqual(Hotkey.hotkeyToCombo("ctrl + shift"), {29, 42})
        self.assertEqual(Hotkey.hotkeyToCombo([29, 42]), {29, 42})
        
if __name__ == "__main__":
    unittest.main()