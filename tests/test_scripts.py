import importlib
import os
import sys
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
sys.path.append(ROOT_DIR)

DDHF_SCRIPTS = filter(lambda fname: os.path.basename(fname).startswith('ddhf_'), os.listdir())

class DDHFScriptsTestCase(unittest.TestCase):
    """
    Smoke tests ensuring ddhf scripts can be loaded correctly.
    """

    @staticmethod
    def define_script_test(test_case, script_name):
        def _excavation_test(self):
            try:
                importlib.import_module(script_name)
            except:
                self.fail(script_name)
        _excavation_test.__name__ = "test_%s" % script_name
        _excavation_test.__doc__ = f"{script_name} script"
        setattr(test_case, _excavation_test.__name__, _excavation_test)

for script in DDHF_SCRIPTS:
    script_name = script[:-3] # strip extension
    DDHFScriptsTestCase.define_script_test(DDHFScriptsTestCase, script_name)

if __name__ == '__main__':
    unittest.main()
