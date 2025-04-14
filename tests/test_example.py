import os
import shutil
from types import SimpleNamespace
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_DIR = os.path.join(TESTS_DIR, "_scratch")

from autoarchaeologist.__main__ import perform_excavation


def _dir_to_listing(absolute_dir, /, kind):
    assert os.path.isabs(absolute_dir)
    _, dirs, files = list(os.walk(absolute_dir))[0]
    match kind:
        case 'dirs':
            return sorted(dirs)
        case 'files':
            return set(files)
        case _:
            raise NotImplementedError()


class Test_Example_BasicHtml(unittest.TestCase):
    """
    Ensure run_example produces expected HTML files for the example input.
    """

    ARGS = None

    @classmethod
    def setUpClass(cls):
        args = SimpleNamespace(
            dir=SCRATCH_DIR,
            filename="examples/30001393.bin",
            excavator="examples.excavations.showcase",
        )
        shutil.rmtree(args.dir, ignore_errors=True)
        os.makedirs(args.dir, exist_ok=True)
        cls.ARGS = args

    def test_produces_top_level_index(self):
        ctx = perform_excavation(self.ARGS)
        ctx.produce_html()

        toplevel_filenames = _dir_to_listing(self.ARGS.dir, kind='files')

        self.assertTrue("index.html" in toplevel_filenames)
        self.assertTrue("index.css" in toplevel_filenames)

    def test_produces_digest_directories(self):
        ctx = perform_excavation(self.ARGS)
        ctx.produce_html()

        toplevel_dirnames = _dir_to_listing(self.ARGS.dir, kind='dirs')

        self.assertEqual(toplevel_dirnames, ['08', 'bf', 'fa'])


if __name__ == '__main__':
    unittest.main()
