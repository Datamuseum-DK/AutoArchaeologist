#!/usr/bin/env python3

''' Handle command line argument files '''

import os

from . import plain_file
from . import imd_file
from . import simh_tap_file

def argv_file(excavation, fn):
    ''' Process extra command line arguments '''
    if not os.path.isfile(fn) or not os.path.getsize(fn):
        return None
    print("Loading", fn)
    ext = os.path.splitext(fn)
    if ext[1] in (".tap", ".TAP"):
        this = simh_tap_file.SimhTapContainer(filename = fn)
    elif ext[1] in (".imd", ".IMD"):
        this = imd_file.ImdContainer(filename = fn)
    else:
        this = plain_file.PlainFileArtifact(fn)
    return excavation.add_top_artifact(this, description=fn, dup_ok=True)
