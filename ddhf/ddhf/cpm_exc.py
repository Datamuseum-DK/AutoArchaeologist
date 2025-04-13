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

class TextFile(textfiles.TextFile):
    VERBOSE = False

class CpmDS2089(type_case.DS2089):
    def __init__(self):
        super().__init__()
        self.set_slug(0x00, " ", "«nul»", self.IGNORE)
        self.set_slug(0x0d, " ", "")
        self.set_slug(0x1a, " ", "«eof»", self.EOF)

def std_cpm_excavation(exc):
    ''' Standard CP/M excavation '''

    #exc.type_case = type_case.DS2089()
    exc.type_case = CpmDS2089()
    exc.add_examiner(fs_auto.ProbeCpmFileSystem)
    exc.add_examiner(TextFile)
    exc.add_examiner(samesame.SameSame)
