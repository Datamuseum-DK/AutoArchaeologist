#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Rational R1000 Ada Assembly Files
   ---------------------------------

   Call out to PyReveng3 for disassembling assistance

   (https://github.com/bsdphk/PyReveng3)
'''

import sys
import subprocess

from ...generic import pyreveng3

class R1kAssyFile():
    ''' Binary instruction segment '''

    def __init__(self, this):
        if this[:3].tobytes() not in (b'\x00\x0f\x58', b'\x00\x0f\x59',):
            return
        if len(this) > 128<<10:
            return
        if not pyreveng3.PYREVENG3:
            return
        print("?R1K_ASSY", this)
        this.add_note(this[2:4].tobytes().hex() + "_R1K_CODE")
        if not this[22] and not this[23]:
            this.add_note("Zero_Subprog_0xb")
        if this[12] or this[13]:
            this.add_note("ELAB_segment_table")

        tf1 = this.tmpfile_for()
        this.writetofile(open(tf1.filename, "wb"))

        tf2 = this.add_utf8_interpretation("Disassembly")
        sys.stdout.flush()
        sys.stderr.flush()
        try:
            subprocess.run(
                [
                    "python3",
                    pyreveng3.PYREVENG3 + "/examples/R1000_400/example_ada.py",
                    tf1.filename,
                    tf2.filename,
                ],
                check = True,
            )
        except subprocess.CalledProcessError as err:
            print("Disassembly failed", this, err)
