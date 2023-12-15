import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

from autoinput import *

class TestAutoInput(unittest.TestCase):    
    def test_keyToScanCode(self):
        self.assertEqual(keyToScanCode("ctrl+shift"), [29,42])
        self.assertEqual(keyToScanCode("ctrl + shift"), [29,42])
        self.assertEqual(keyToScanCode("shift"), 42)
        self.assertEqual(keyToScanCode("right shift"), 54)
        self.assertEqual(keyToScanCode("ctrl+right shift"), [29, 54])
        self.assertEqual(keyToScanCode("right shift + right shift"), [54, 54])
        
if __name__ == "__main__":
    unittest.main()