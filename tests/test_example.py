import os
import shutil
from types import SimpleNamespace
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_DIR = os.path.join(TESTS_DIR, "_scratch")

from autoarchaeologist.__main__ import perform_excavation


class Test_Example_BasicHtml(unittest.TestCase):
    """
    Ensure run_example produces expected HTML files for the example input.
    """

    DIR_TREE = None

    @classmethod
    def setUpClass(cls):
        args = SimpleNamespace(
            dir=SCRATCH_DIR,
            filename="examples/30001393.bin",
            excavator="examples.showcase",
        )
        shutil.rmtree(args.dir, ignore_errors=True)
        os.makedirs(args.dir, exist_ok=True)
        ctx = perform_excavation(args)
        ctx.produce_html()
        cls.DIR_TREE = list(os.walk(args.dir))

    def toplevel(self):
        return self.__class__.DIR_TREE[0]

    def toplevel_dirnames(self):
        _, dirs, __ = self.toplevel()
        dirs.sort()
        return dirs

    def toplevel_filenames(self):
        _, __, filenames = self.toplevel()
        return filenames

    def test_produces_top_level_index(self):
        toplevel_filenames = self.toplevel_filenames()
        self.assertTrue("index.html" in toplevel_filenames)
        self.assertTrue("index.css" in toplevel_filenames)

    def test_produces_digest_directories(self):
        toplevel_dirnames = self.toplevel_dirnames()
        self.assertEqual(toplevel_dirnames, ['08', '79', 'fa'])
