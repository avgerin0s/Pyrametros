from ..cfile import CFile
from common import *
import unittest

class TestCFile(unittest.TestCase):
    def setUp(self):
        # Back up
        backup("cfile.txt")

    def tearDown(self):
        # If tests fail we want the file to be untouched
        restore("cfile.txt")

    def test_read(self):
        read = CFile(static_path("cfile.txt"), "read", deliminer_string="# %(begin_or_end)s %(tag)s", readonly=True)

        # Reads the lines it should
        self.assertIn('legend', "\n".join(read.search("rock'n'roll")))

        # Not the lines it shouldn't
        self.assertNotIn("Fuller",  "\n".join(read.contents()))

    def test_read_only(self):
        read = CFile(static_path("cfile.txt"), "read", deliminer_string="# %(begin_or_end)s %(tag)s", readonly=True)

        # Readonly should prevent anyone from writing
        with self.assertRaises(Exception):
            read.push_line("test")

        with self.assertRaises(Exception):
            read.push_lines(["test"])

    def test_write(self):
        # Issert some text
        write = CFile(static_path("cfile.txt"), "write", deliminer_string="# %(begin_or_end)s %(tag)s")
        write.push_line("Schene is now in the rebel's base")
        write.push_lines(["Spoiler alert", "the star wars movies"])
        write.flush()

        # XXX: also test that the lines are i the right order
        with open(static_path("cfile.txt")) as f:
            self.assertIn( "Spoiler alert\n", f.readlines())

        # We havent added anything since last flush so this will remove the text
        write.flush()

        with open(static_path("cfile.txt")) as f:
            self.assertNotIn("Spoiler alert", f.readlines())

    def test_read_write(self):
        rw = CFile(static_path("cfile.txt"), "rw", deliminer_string="# %(begin_or_end)s %(tag)s")
        rw.push_lines([i.replace("sandbagged", "butt fucked") for i in rw.contents(real=True)])

        # Not flushed: changes in virtual file not in real one
        self.assertIn("You butt fucked me, yes.", rw.contents(real=False))
        self.assertNotIn("You butt fucked me, yes.", rw.contents(real=True))

        rw.flush()

        # Flushed: virtual file empty, real file has changes
        self.assertEquals(rw.contents(real=False), [])
        self.assertIn("You butt fucked me, yes.", rw.contents(real=True))


        rw.push_lines([i.replace("butt fucked", "sandbagged") for i in rw.contents(real=True)])
        rw.flush()

        # Reverted to the previous state
        with open(static_path("cfile.txt")) as f:
            self.assertIn("You sandbagged me, yes.\n", f.readlines())


if __name__ == "__main__":
    unittest.main()
