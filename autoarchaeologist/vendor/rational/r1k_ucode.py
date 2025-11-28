#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

from ...generic import hexdump

from . import r1k_disass

class R1K_Ucode_File():

    def __init__(self, this):

        good = False
        for i in this.iter_types():
            if i[-6:] == "_UCODE":
                good = True
        if not good:
            return

        print(this, "UCODE")
        this.add_type("UCODE")

        r1k_disass.R1kDisass(
            this,
            "UCODE/disass_ucode.py",
        )
