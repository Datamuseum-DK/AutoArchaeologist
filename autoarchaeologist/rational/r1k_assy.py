'''
   Rational R1000 Ada Assembly Files
   ---------------------------------

   Call out to PyReveng3 for disassembling assistance

   (https://github.com/bsdphk/PyReveng3)
'''

import os
import sys
import subprocess
import html

import autoarchaeologist

class R1K_Assy_File():
    ''' Binary instruction segment '''

    def __init__(self, this):
        if this[:3].tobytes() not in (b'\x00\x0f\x58', b'\x00\x0f\x59',):
            return
        if len(this) > 128<<10:
            return
        if not autoarchaeologist.PYREVENG3:
            return
        print("?R1K_ASSY", this)
        this.add_note(this[2:4].tobytes().hex() + "_R1K_CODE")
        if not this[22] and not this[23]:
            this.add_note("Zero_Subprog_0xb")
        if this[12] or this[13]:
            this.add_note("ELAB_segment_table")

        tf1 = this.filename_for(suf=".bin.tmp")
        this.writetofile(open(tf1.filename, "wb"))

        self.tf2 = this.filename_for(suf=".dis.tmp")
        sys.stdout.flush()
        sys.stderr.flush()
        try:
            subprocess.run(
                [
                    "python3",
                    autoarchaeologist.PYREVENG3 + "/examples/R1000_400/example_ada.py",
                    tf1.filename,
                    self.tf2.filename,
                ],
                check = True,
            )
        except subprocess.CalledProcessError as err:
            print("Disassmbly failed", this, err)
            return
        this.add_interpretation(self, self.render_disass)
        os.remove(tf1.filename)

    def render_disass(self, fo, _this):
        ''' Emit PyReveng3's output '''
        fo.write("<H3>Disassembly</H3>\n")
        fo.write("<pre>\n")
        for i in open(self.tf2.filename):
            fo.write(html.escape(i))
        fo.write("</pre>\n")
        os.remove(self.tf2.filename)
