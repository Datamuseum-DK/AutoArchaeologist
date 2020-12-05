'''
   Rational R1000 Ada Assembly Files
   ---------------------------------

   Call out to PyReveng3 for disassembling assistance

   (https://github.com/bsdphk/PyReveng3)
'''

import subprocess
import tempfile
import html

import autoarchaeologist

class R1K_Assy_File():
    ''' Binary instruction segment '''

    def __init__(self, this):
        if this[:3].tobytes() != b'\x00\x0f\x58':
            return
        if len(this) > 128<<10:
            return
        if not autoarchaeologist.PYREVENG3:
            return
        print("?R1K_ASSY", this)
        this.add_note("R1K_CODE")

        tf1 = tempfile.NamedTemporaryFile()
        this.writetofile(tf1)
        tf1.flush()

        self.tf2 = tempfile.NamedTemporaryFile()
        print("NAME", tf1.name, self.tf2.name)
        subprocess.run(
            [
                "python3",
                autoarchaeologist.PYREVENG3 + "/examples/R1000_400/example_ada.py",
                tf1.name,
                self.tf2.name,
            ],
            check = True,
        )
        this.add_interpretation(self, self.render_disass)

    def render_disass(self, fo, _this):
        ''' Emit PyReveng3's output '''
        fo.write("<H3>Disassembly</H3>\n")
        fo.write("<pre>\n")
        for i in self.tf2:
            j = i.decode("utf8")
            fo.write(html.escape(j))
        fo.write("</pre>\n")
