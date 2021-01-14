'''
   Rational R1000 M200 68K20 Assembly Files
   ----------------------------------------

   Call out to PyReveng3 for disassembling assistance

   (https://github.com/bsdphk/PyReveng3)
'''

import sys
import subprocess

import autoarchaeologist

class R1kM200File():
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

        tf1 = this.tmpfile_for()
        this.writetofile(open(tf1.filename, "wb"))

        tf2 = this.add_utf8_interpretation("Disassembly")
        sys.stdout.flush()
        sys.stderr.flush()
        try:
            subprocess.run(
                [
                    "python3",
                    autoarchaeologist.PYREVENG3 + "/examples/R1000_400/example_m200.py",
                    tf1.filename,
                    tf2.filename,
                ],
                check = True,
            )
        except subprocess.CalledProcessError as err:
            print("Disassmbly failed", this, err)
