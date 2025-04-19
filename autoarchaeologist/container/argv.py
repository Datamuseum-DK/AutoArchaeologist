#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' Handle command line argument files '''

import os

from . import plain_file
from . import imd_file
from . import d64_file
from . import simh_tap_file
# from . import floppytools

def argv_file(excavation, fn):
    ''' Process extra command line arguments '''
    if not os.path.isfile(fn) or not os.path.getsize(fn):
        return None
    print("Loading", fn)
    ext = os.path.splitext(fn)
    if ext[1] in (".tap", ".TAP",):
        this = simh_tap_file.SimhTapContainer(excavation, filename = fn)
    elif ext[1] in (".imd", ".IMD",):
        this = imd_file.ImdContainer(excavation, filename = fn)
    elif ext[1] in (".d64", ".D64",):
        this = d64_file.D64Container(excavation, filename = fn)
    #elif ext[1] in (".cache",):
    #    this = floppytools.FloppyToolsContainer(excavation, filename = fn)
    else:
        this = plain_file.PlainFileArtifact(fn)
    return excavation.add_top_artifact(this, description=fn, dup_ok=True)
