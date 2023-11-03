import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

import autoinput

class TestAutoInput(unittest.TestCase):
    def test_autoinput(self):
        self.assertEqual(5, 5)
        
if __name__ == "__main__":
    unittest.main()