import unittest
import sys
import test_util

sys.path.append(str(test_util.PROJECT_ROOT))
from src import dcli


class TestCommand(unittest.TestCase):

    def testCommandName(self):
        command_name = "test_command"

        @dcli.command(command_name)
        def MyCommand():
            pass

        self.assertEqual(str(MyCommand), command_name)

    def testPositionalArgs(self):
        @dcli.command(
            "testPositionalArgs",
            dcli.arg("hi", nargs="*")
        )
        def main(ns):
            return getattr(ns, "hi")

        self.assertEqual(main([]), [])
        self.assertEqual(main(["123", "453"]), ["123", "453"])

    def testReturnValue(self):
        @dcli.command("bool-check",
                      dcli.arg("-t", dest="val", default=False, action="store_true"))
        def returnBool(ns):
            return getattr(ns, "val")

        self.assertFalse(returnBool([]))
        self.assertTrue(returnBool(["-t"]))

        @dcli.command("int-check",
                      dcli.arg("-t", dest="val", default=0, type=int))
        def returnInteger(ns):
            return getattr(ns, "val")

        self.assertEqual(returnInteger([]), 0)
        self.assertEqual(returnInteger(["-t", "123"]), 123)

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
        cross_sub = False

        @dcli.command(
            "skip-command",
            skippable=True
        )
        def rootCmd(namespace):
            # should not go here
            self.assertFalse(True)

        @dcli.command(
            "test",
            dcli.arg("-t", dest="dest", action="store", type=int),
            parent=rootCmd
        )
        def testCmd(namespace):
            nonlocal val, cross_sub
            cross_sub = True
            self.assertEqual(getattr(namespace, "dest"), val)

        val = None
        cross_sub = False
        rootCmd(["test"])
        self.assertTrue(cross_sub)

        val = 123
        cross_sub = False
        rootCmd(["test", "-t", str(val)])
        self.assertTrue(cross_sub)

    def testNestedCommandWithoutSkip(self):
        val = None
        cross_root = False
        cross_sub = False

        @dcli.command(
            "skip-command",
            skippable=False
        )
        def rootCmd(namespace):
            nonlocal val, cross_root
            cross_root = True
            self.assertEqual(getattr(namespace, "dest"), val)

        @dcli.command(
            "test",
            dcli.arg("-t", dest="dest", action="store", type=int),
            parent=rootCmd
        )
        def testCmd(namespace):
            nonlocal val, cross_sub
            cross_sub = True
            self.assertEqual(getattr(namespace, "dest"), val)

        val = None
        cross_root = False
        cross_sub = False
        rootCmd(["test"])
        self.assertTrue(cross_root)
        self.assertTrue(cross_sub)

        val = 123
        cross_root = False
        cross_sub = False
        rootCmd(["test", "-t", str(val)])
        self.assertTrue(cross_root)
        self.assertTrue(cross_sub)

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

    def testManualAddSubCommandCheck(self):
        @dcli.command("root")
        def MyCommand(_):
            pass

        @dcli.command("sub")
        def SubCommand1(_):
            pass

        @dcli.command("sub")
        def SubCommand2(_):
            pass

        self.assertRaises(AssertionError, MyCommand.addSubCommand, 123)
        MyCommand.addSubCommand(SubCommand1)
        # add a duplicate name of command is invalid.
        self.assertRaises(AssertionError, MyCommand.addSubCommand, SubCommand2)

    def testManualAddSubCommand(self):
        cross_sub1 = False
        cross_sub2 = False

        @dcli.command("root")
        def MyCommand(_):
            pass

        @dcli.command(
            "sub1",
            dcli.arg("-f", dest="dest", default=False, action="store_true")
        )
        def SubCommand1(ns):
            nonlocal cross_sub1
            cross_sub1 = True
            return getattr(ns, "dest")

        @dcli.command(
            "sub2",
            dcli.arg("-f", dest="dest", default=False, action="store_true")
        )
        def SubCommand2(ns):
            nonlocal cross_sub2
            cross_sub2 = True
            return getattr(ns, "dest")

        MyCommand.addSubCommand(SubCommand1)
        MyCommand.addSubCommand(SubCommand2)

        cross_sub1 = False
        cross_sub2 = False
        self.assertTrue(MyCommand(["sub1", "-f"]))
        self.assertTrue(cross_sub1)
        self.assertFalse(cross_sub2)

        cross_sub1 = False
        cross_sub2 = False
        MyCommand(["sub2"])
        self.assertTrue(MyCommand(["sub2", "-f"]))
        self.assertFalse(cross_sub1)
        self.assertTrue(cross_sub2)


if __name__ == "__main__":
    unittest.main()
