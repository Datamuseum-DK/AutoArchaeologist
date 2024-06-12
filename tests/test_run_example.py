import importlib
import os
import shutil
import sys
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(TESTS_DIR, ".."))

# run_example is technically outside the package so force its import
sys.path.append(ROOT_DIR)
from run_example import process_example
from autoarchaeologist.base.artifact import ArtifactBase, ArtifactStream
sys.path.remove(ROOT_DIR)

SCRATCH_DIR = os.path.join(TESTS_DIR, "_scratch")

def scratch_path(path):
    return os.path.join(SCRATCH_DIR, path)

class RunExampleBasicHtml(unittest.TestCase):
    """
    Ensure run_example produces expected HTML files for the example input.
    """

    DIR_TREE = None

    @classmethod
    def setUpClass(cls):
        shutil.rmtree(SCRATCH_DIR)
        os.makedirs(SCRATCH_DIR, exist_ok=True)
        ctx = process_example(html_dir=SCRATCH_DIR)
        ctx.produce_html()
        cls.DIR_TREE = list(os.walk(SCRATCH_DIR))

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

class RunExampleBasicArtifacts(unittest.TestCase):
    """
    Ensure run_example excavates the expected artifacts for the example input.
    """

    CTX = None

    @classmethod
    def setUpClass(cls):
        cls.CTX = process_example(html_dir=SCRATCH_DIR)

    def assertArtifactIsChild(self, artifact, parent):
        assert issubclass(artifact.__class__, ArtifactBase)
        self.assertEqual(list(artifact.parents), [parent])

    def excavation(self):
        return self.__class__.CTX

    def test_excavated_three_total_artifacts(self):
        arfifact_hash_keys = list(self.excavation().hashes.keys())
        self.assertEqual(len(arfifact_hash_keys), 3)

    def test_excavated_one_top_level_artifact(self):
        excavatoin_child_count = len(self.excavation().children)
        self.assertEqual(excavatoin_child_count, 1)

    def test_produces_top_level_artifact(self):
        excavation = self.excavation()
        artifact = self.excavation().children[0]
        self.assertIsInstance(artifact, ArtifactStream)
        self.assertEqual(artifact.digest, '083a3d5e3098aec38ee5d9bc9f9880d3026e120ff8f058782d49ee3ccafd2a6c')

    def test_produces_top_level_artifact_whose_parent_is_excavation(self):
        artifact = self.excavation().children[0]
        self.assertArtifactIsChild(artifact, self.excavation())

    def test_produces_two_children_of_the_top_level(self):
        artifact = self.excavation().children[0]
        artifact_children = sorted(artifact.children, key=lambda a: a.digest)
        self.assertEqual(len(artifact_children), 2)
        self.assertTrue(artifact_children[0].digest.startswith('79'))
        self.assertArtifactIsChild(artifact_children[0], artifact)
        self.assertTrue(artifact_children[1].digest.startswith('fa'))
        self.assertArtifactIsChild(artifact_children[1], artifact)

if __name__ == '__main__':
    unittest.main()
