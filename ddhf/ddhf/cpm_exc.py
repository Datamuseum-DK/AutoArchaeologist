#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Standardized CP/M Excavation stuff
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.base import type_case
from autoarchaeologist.generic import samesame
from autoarchaeologist.generic import textfiles
from autoarchaeologist.os.cpm import fs_auto

from . import DDHFExcavation

class CpmDS2089(type_case.DS2089):
    ''' ... '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x00, " ", "«nul»", self.IGNORE)
        self.set_slug(0x0d, " ", "")
        self.set_slug(0x1a, " ", "«eof»", self.EOF)

class DdhfExcavationCpm(DDHFExcavation):
    ''' ... '''

    MEDIA_TYPES = (
        '5¼" Floppy Disk',
        '8" Floppy Disk',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type_case = CpmDS2089()
        self.add_examiner(fs_auto.ProbeCpmFileSystem)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)

def std_cpm_excavation(exc):
    ''' Standard CP/M excavation '''

    #exc.type_case = type_case.DS2089()
    exc.type_case = CpmDS2089()
    exc.add_examiner(fs_auto.ProbeCpmFileSystem)
    exc.add_examiner(textfiles.TextFile)
    exc.add_examiner(samesame.SameSame)
