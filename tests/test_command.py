import unittest
import sys
import test_util

sys.path.append(str(test_util.DCLI_ROOT))
import dcli


class TestCommand(unittest.TestCase):

    def testCommandWrapper(self):
        val = None
        @dcli.command(
            "test-command",
            dcli.arg("-t", "--test", dest="dest", action="store", type=int),
        )
        def testCmd(namespace):
            nonlocal val
            self.assertTrue(hasattr(namespace, "dest"))
            self.assertEqual(getattr(namespace, "dest"), val)

        val = None
        testCmd([])

        val = 123
        testCmd(["-t", str(val)])
        testCmd(["--test", str(val)])

    def testNestedCommandWithSkip(self):
        val = None

        @dcli.command(
            "skip-command",
            skippable=True
        )
        def rootCmd(namespace):
            # should not go here
            self.assertTrue(False)

        @dcli.command(
            "test",
            dcli.arg("-t", "--test", dest="dest", action="store", type=int),
            parent=rootCmd
        )
        def testCmd(namespace):
            nonlocal val
            self.assertTrue(hasattr(namespace, "dest"))
            self.assertEqual(getattr(namespace, "dest"), val)

        val = None
        testCmd([])
        rootCmd(["test"])

        val = 123
        rootCmd(["test", "-t", str(val)])
        rootCmd(["test", "--test", str(val)])
        testCmd(["-t", str(val)])
        testCmd(["--test", str(val)])

    def testNestedCommandWithoutSkip(self):
        val = None
        cross_root = False

        @dcli.command(
            "skip-command",
            skippable=False
        )
        def rootCmd(namespace):
            nonlocal val, cross_root
            cross_root = True
            self.assertTrue(hasattr(namespace, "dest"))
            self.assertEqual(getattr(namespace, "dest"), val)

        @dcli.command(
            "test",
            dcli.arg("-t", "--test", dest="dest", action="store", type=int),
            parent=rootCmd
        )
        def testCmd(namespace):
            nonlocal val
            self.assertTrue(hasattr(namespace, "dest"))
            self.assertEqual(getattr(namespace, "dest"), val)

        val = None
        cross_root = False
        testCmd([])
        rootCmd(["test"])
        self.assertTrue(cross_root)

        val = 123
        cross_root = False
        rootCmd(["test", "-t", str(val)])
        rootCmd(["test", "--test", str(val)])
        testCmd(["-t", str(val)])
        testCmd(["--test", str(val)])
        self.assertTrue(cross_root)

    def testNestedCommandWithoutNeedSub(self):
        has_root = False
        root_val = None
        test_val = None

        @dcli.command(
            "root",
            dcli.arg("--root", dest="root", action="store", type=int),
            skippable=False,
            need_sub=False
        )
        def rootCmd(namespace):
            nonlocal root_val, has_root
            if has_root:
              self.assertTrue(hasattr(namespace, "root"))
              self.assertEqual(getattr(namespace, "root"), root_val)

        @dcli.command(
            "sub",
            dcli.arg("--test", dest="test", action="store", type=int),
            parent=rootCmd
        )
        def testCmd(namespace):
            nonlocal test_val
            self.assertTrue(hasattr(namespace, "test"))
            self.assertEqual(getattr(namespace, "test"), test_val)

        root_val = None
        has_root = True
        rootCmd([])
        root_val = 123
        rootCmd(["--root", str(root_val)])

        test_val = None
        has_root = False
        rootCmd(["sub"])
        test_val = 123
        rootCmd(["sub", "--test", str(test_val)])

if __name__ == "__main__":
    unittest.main() 