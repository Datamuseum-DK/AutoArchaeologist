#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   R1000 Microcode
   ===============
'''

from . import r1k_disass

class R1kM200UcodeFile():

    ''' Disassemble R1000/M200-M400 microcode '''

    def __init__(self, this):

        good = False
        for i in this.iter_types():
            if i[-10:] == "M200_UCODE":
                good = True
        if not good:
            return

        print(this, "M200_UCODE")

        r1k_disass.R1kDisass(this, "UCODE/disass_ucode.py")

ALL = [
    R1kM200UcodeFile,
]
