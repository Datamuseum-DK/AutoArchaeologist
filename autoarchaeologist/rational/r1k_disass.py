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

        tf2 = this.add_utf8_interpretation("Disassembly")
        sys.stdout.flush()
        sys.stderr.flush()

        path = os.path.join(R1KDISASS, script)

        try:
            subprocess.run(
                [
                    "python3",
                    "-u",
                    path,
                    "-AutoArchaeologist",
                    this.digest[:16],
                    tf1.filename,
                    tf2.filename,
                ],
                check = True,
            )
        except subprocess.CalledProcessError as err:
            print("Disassmbly failed", this)
            print("    Script:", script)
            print("    Error:", err)
