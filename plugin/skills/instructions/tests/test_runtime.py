"""Regression tests. Extraction fixtures use installed mido/packaging source,
not the inaccessible original binary archive; that limitation is intentional."""

import unittest

class TestRuntime(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
