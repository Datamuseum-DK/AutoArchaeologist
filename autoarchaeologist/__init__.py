
import os

from .excavation import Excavation, DuplicateArtifact
from .artifact import DuplicateName
from .record import Record
from .namespace import NameSpace

PYREVENG3 = os.environ.get("AUTOARCHAEOLOGIST_PYREVENG3")
if not PYREVENG3 or not os.path.isdir(PYREVENG3):
    PYREVENG3 = str(os.environ.get("HOME")) + "/PyReveng3/"
if not PYREVENG3 or not os.path.isdir(PYREVENG3):
    PYREVENG3 = str(os.environ.get("HOME")) + "/Proj/PyReveng3/"
if not PYREVENG3 or not os.path.isdir(PYREVENG3):
    PYREVENG3 = None
