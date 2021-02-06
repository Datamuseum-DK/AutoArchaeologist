'''
   Callout to PyReveng3 for disassembly
   ------------------------------------
'''

import os
import sys
import subprocess

import autoarchaeologist

class PyReveng3():
    ''' ... '''

    def __init__(self, this, script):
        if not autoarchaeologist.PYREVENG3:
            return

        tf1 = this.tmpfile_for()
        this.writetofile(open(tf1.filename, "wb"))

        tf2 = this.add_utf8_interpretation("Disassembly")
        sys.stdout.flush()
        sys.stderr.flush()

        path = os.path.join(autoarchaeologist.PYREVENG3, script)

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
