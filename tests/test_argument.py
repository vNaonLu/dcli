import unittest
import sys
import test_util

sys.path.append(str(test_util.DCLI_ROOT))
import dcli

class TestArgument(unittest.TestCase):

    def testArgumentForward(self):
        wrapper = dcli.arg("-t", "--test", action="test")
        self.assertEqual(len(wrapper.args), 2)
        self.assertEqual(wrapper.args[0], "-t")
        self.assertEqual(wrapper.args[1], "--test")
        self.assertTrue("action" in wrapper.kwargs)
        self.assertEqual(wrapper.kwargs["action"], "test")

    def testPassToArgParser(self):
        import argparse
        parser = argparse.ArgumentParser("test", exit_on_error=False)
        wrapper = dcli.arg("-t", "--test", dest="dest",
                           type=int, action="store", nargs="?")
        parser.add_argument(*wrapper.args, **wrapper.kwargs)

        arg = parser.parse_args(["-t", "123"])
        self.assertTrue(hasattr(arg, "dest"))
        self.assertEqual(getattr(arg, "dest"), 123)

        arg = parser.parse_args(["--test", "123"])
        self.assertTrue(hasattr(arg, "dest"))
        self.assertEqual(getattr(arg, "dest"), 123)

        arg = parser.parse_args([])
        self.assertTrue(hasattr(arg, "dest"))
        self.assertEqual(getattr(arg, "dest"), None)

if __name__ == "__main__":
    unittest.main() 