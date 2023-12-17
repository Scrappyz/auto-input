import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

from autoinput import *

class TestAutoInput(unittest.TestCase):    
    def test_keyToScanCode(self):
        self.assertEqual(Hotkey.splitKeys("shift"), ["shift"])
        self.assertEqual(Hotkey.splitKeys("ctrl+shift"), ["ctrl", "shift"])
        self.assertEqual(Hotkey.splitKeys("ctrl + shift"), ["ctrl", "shift"])
        self.assertEqual(Hotkey.splitKeys("ctrl   +   shift"), ["ctrl", "shift"])
        self.assertEqual(Hotkey.splitKeys("ctrl + right shift"), ["ctrl", "right shift"])
        self.assertEqual(Hotkey.splitKeys("right ctrl + right shift"), ["right ctrl", "right shift"])
        
if __name__ == "__main__":
    unittest.main()