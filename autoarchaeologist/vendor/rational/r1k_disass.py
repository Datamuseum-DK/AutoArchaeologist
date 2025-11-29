#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Callout to PyReveng3 for disassembly
   ------------------------------------
'''

import os
import sys
import subprocess

R1KDISASS = os.environ.get("AUTOARCHAEOLOGIST_R1KDISASS")
if not R1KDISASS or not os.path.isdir(R1KDISASS):
    R1KDISASS = str(os.environ.get("HOME")) + "/R1000.Disassembly/"
if not R1KDISASS or not os.path.isdir(R1KDISASS):
    R1KDISASS = str(os.environ.get("HOME")) + "/Proj/R1000.Disassembly/"
if not R1KDISASS or not os.path.isdir(R1KDISASS):
    R1KDISASS = None

class R1kDisass():
    ''' ... '''

    def __init__(self, this, script):
        if not R1KDISASS:
            return

        tf1 = this.tmpfile_for()
        this.writetofile(open(tf1.filename, "wb"))

        tf2 = this.tmpfile_for()

        path = os.path.join(R1KDISASS, script)

        s = subprocess.run(
            [
                "python3",
                "-u",
                path,
                "-AutoArchaeologist",
                this.digest[:16],
                tf1.filename,
                tf2.filename,
            ],
            capture_output=True,
        )
        if not s.returncode:
            if script in (
                "DFS/disass_dfs.py",
                "UCODE/disass_ucode.py",
            ):
                out = this.add_html_interpretation("Disassembly")
            else:
                out = this.add_utf8_interpretation("Disassembly")
            with open(out.filename, "wb") as ofile:
                with open(tf2.filename, "rb") as ifile:
                    ofile.write(ifile.read())
            if s.stderr:
                out = this.add_utf8_interpretation("Disassembly stderr")
                with open(out.filename, "wb") as ofile:
                    ofile.write(s.stderr)
            if s.stdout:
                out = this.add_utf8_interpretation("Disassembly stdout")
                with open(out.filename, "wb") as ofile:
                    ofile.write(s.stdout)
            return
        this.add_comment(self.__class__.__name__ + " Failed")
        if s.stderr:
            this.add_comment(s.stderr.decode("utf8"))


