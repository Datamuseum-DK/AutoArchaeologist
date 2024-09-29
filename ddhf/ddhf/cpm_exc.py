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
from autoarchaeologist.DigitalResearch import cpm

cpm.cpm_filename_typecase.set_slug(0x5f, '_', '_')
cpm.cpm_filename_typecase.set_slug(0x3b, ';', ';')

def std_cpm_excavation(exc):
    ''' Standard CP/M excavation '''

    exc.type_case = type_case.DS2089Cpm()
    exc.add_examiner(cpm.CpmFileSystem)
    exc.add_examiner(textfiles.TextFile)
    exc.add_examiner(samesame.SameSame)
