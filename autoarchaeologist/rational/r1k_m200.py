'''
   Rational R1000 M200 68K20 Assembly Files
   ----------------------------------------

   Call out to PyReveng3 for disassembling assistance

   (https://github.com/bsdphk/PyReveng3)
'''

import sys
import subprocess
import tempfile
import html

import autoarchaeologist

class R1K_M200_File():
    ''' IOC program '''

    def __init__(self, this):
        if not autoarchaeologist.PYREVENG3:
            return
        if not this.has_type("M200"):
            return
        sig = this[:6].tobytes().hex()
        if sig != "000400000002":
            print("?R1K_M200", this, len(this), sig, this.name)
            return

        tf1 = tempfile.NamedTemporaryFile()
        this.writetofile(tf1)
        tf1.flush()

        self.tf2 = tempfile.NamedTemporaryFile(dir=this.top.html_dir)
        # print("NAME", tf1.name, self.tf2.name)
        sys.stdout.flush()
        sys.stderr.flush()
        try:
            subprocess.run(
                [
                    "python3",
                    autoarchaeologist.PYREVENG3 + "/examples/R1000_400/example_m200.py",
                    tf1.name,
                    self.tf2.name,
                ],
                check = True,
            )
        except subprocess.CalledProcessError as e:
            print("Disassmbly failed", this, e)
            return
        this.add_interpretation(self, self.render_disass)

    def render_disass(self, fo, _this):
        ''' Emit PyReveng3's output '''
        fo.write("<H3>Disassembly</H3>\n")
        fo.write("<pre>\n")
        for i in self.tf2:
            j = i.decode("utf8")
            fo.write(html.escape(j))
        fo.write("</pre>\n")
