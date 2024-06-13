import unittest

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "../.."))
sys.path.append(ROOT_DIR)

from autoarchaeologist import excavators
from autoarchaeologist.base import excavation

class ExcavationsSmoke(unittest.TestCase):
    """
    Smoke tests ensuring defined excavations are exported correctly.
    """

    @staticmethod
    def define_excavation_test(test_case, excavator_name):
        def _excavation_test(self):
            Excavation = None
            try:
                Excavation = excavators.excavator_by_name(excavator_name)
            except:
                self.fail(f'unable to retriveve excavator "{excavator_name}"')
            self.assertTrue(issubclass(Excavation, excavation.Excavation))

        _excavation_test.__name__ = "test_%s" % excavator_name
        _excavation_test.__doc__ = f"{excavator_name} smoke test"
        setattr(test_case, _excavation_test.__name__, _excavation_test)

for excavator_name in excavators.__all__:
    ExcavationsSmoke.define_excavation_test(ExcavationsSmoke, excavator_name)

if __name__ == '__main__':
    unittest.main()
