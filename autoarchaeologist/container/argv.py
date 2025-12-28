#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' Handle command line argument files '''

import os

import ddhf_bitstore_metadata

from . import plain_file
from . import imd_file
from . import d64_file
from . import simh_tap_file
from . import simh_crd_file
from . import floppytools
from ..collection import datamuseum_dk

def argv_file(excavation, fn):
    ''' Process extra command line arguments '''
    if not os.path.isfile(fn) or not os.path.getsize(fn):
        return
    print("Loading", fn)
    ext = os.path.splitext(fn)
    try:
        if ext[1] in (".tap", ".TAP", ".9trk",):
            this = simh_tap_file.SimhTapContainer(excavation, filename = fn)
        elif ext[1] in (".imd", ".IMD",):
            try:
                this = imd_file.ImdContainer(excavation, filename = fn)
            except imd_file.BadIMDFile as err:
                print("Bad IMD file", err)
                raise EOFError
        elif ext[1] in (".d64", ".D64", ".d71", ".D71"):
            this = d64_file.D64Container(excavation, filename = fn)
        elif ext[1] in (".crd", ".CRD",):
            try:
                this = simh_crd_file.SimhCrdContainer(excavation, filename = fn)
            except simh_crd_file.BadCRDFile as err:
                print("Bad CRD file", err)
                raise EOFError
        elif ext[1] in (".cache",):
            this = floppytools.FloppyToolsContainer(excavation, filename = fn)
        elif os.path.isfile(fn + ".meta"):
            # Get geometry from .meta file
            this = plain_file.PlainFileArtifact(fn)
            meta = ddhf_bitstore_metadata.internals.metadata.MetadataBase(
                open(fn + ".meta", encoding="utf8").read()
            )
            datamuseum_dk.impose_bitstore_geometry(this, meta.Media.Geometry.val)
        else:
            this = plain_file.PlainFileArtifact(fn)
        that = excavation.add_top_artifact(this, description=fn, dup_ok=True)
        print("Loaded", fn, that)
    except EOFError:
        print(fn, "produced no artifact")
