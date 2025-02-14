import importlib
import os
import shutil
import sys
from types import SimpleNamespace
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_DIR = os.path.join(TESTS_DIR, "_scratch")
ROOT_DIR = os.path.normpath(os.path.join(TESTS_DIR, ".."))

sys.path.append(TESTS_DIR)

from examples import ShowcaseExcacation
from autoarchaeologist.__main__ import process_arguments, perform_excavation, \
    action_for_args
from autoarchaeologist.base.artifact import ArtifactBase, ArtifactStream


class Test_Main_arguments(unittest.TestCase):
    """
    Ensure run_example excavates the expected artifacts for the example input.
    """

    def test_processing_excavator_argument_loads_excavation(self):
        args = process_arguments(SimpleNamespace(
            dir=SCRATCH_DIR,
            filename=os.path.join(ROOT_DIR, 'examples/30001393.bin'),
            excavator='examples.showcase',
        ))

        action_name, action_arg = action_for_args(args)
        self.assertIs(action_name, "excavator")
        self.assertIs(action_arg, ShowcaseExcacation)

class Test_Main_processing(unittest.TestCase):
    """
    Ensure run_example excavates the expected artifacts for the example input.
    """

    ARGS = None

    @classmethod
    def setUpClass(cls):
        args = process_arguments(SimpleNamespace(
            dir=SCRATCH_DIR,
            filename=os.path.join(ROOT_DIR, 'examples/30001393.bin'),
            excavator='examples.showcase',
        ))
        shutil.rmtree(args.dir, ignore_errors=True)
        os.makedirs(args.dir, exist_ok=True)
        # record the unchanging bits against the test case
        cls.ARGS = args

    def assertArtifactIsChild(self, artifact, parent):
        assert issubclass(artifact.__class__, ArtifactBase)
        self.assertEqual(list(artifact.parents), [parent])

    def test_excavated_three_total_artifacts(self):
        excavation = perform_excavation(self.ARGS)

        arfifact_hash_keys = list(excavation.hashes.keys())
        self.assertEqual(len(arfifact_hash_keys), 3)

    def test_excavated_one_top_level_artifact(self):
        excavation = perform_excavation(self.ARGS)

        excavatoin_child_count = len(excavation.children)
        self.assertEqual(excavatoin_child_count, 1)

    def test_produces_top_level_artifact(self):
        excavation = perform_excavation(self.ARGS)

        artifact = excavation.children[0]
        self.assertIsInstance(artifact, ArtifactStream)
        self.assertEqual(artifact.digest, '083a3d5e3098aec38ee5d9bc9f9880d3026e120ff8f058782d49ee3ccafd2a6c')
        self.assertTrue(artifact.digest in excavation.hashes)

    def test_produces_top_level_artifact_whose_parent_is_excavation(self):
        excavation = perform_excavation(self.ARGS)

        artifact = excavation.children[0]
        self.assertArtifactIsChild(artifact, excavation)

    def test_produces_two_children_of_the_top_level(self):
        excavation = perform_excavation(self.ARGS)

        artifact = excavation.children[0]
        artifact_children = sorted(artifact.children, key=lambda a: a.digest)
        self.assertEqual(len(artifact_children), 2)
        self.assertTrue(artifact_children[0].digest in excavation.hashes)
        self.assertTrue(artifact_children[0].digest.startswith('79'))
        self.assertArtifactIsChild(artifact_children[0], artifact)
        self.assertTrue(artifact_children[1].digest in excavation.hashes)
        self.assertTrue(artifact_children[1].digest.startswith('fa'))
        self.assertArtifactIsChild(artifact_children[1], artifact)


if __name__ == '__main__':
    unittest.main()
