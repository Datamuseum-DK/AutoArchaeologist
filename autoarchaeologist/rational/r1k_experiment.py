'''
   Rational R1000 Diagnostic Experiment Files
   ------------------------------------------

   Call out to R1000.Disassembly for disassembling assistance

   (https://github.com/Datamuseum-DK/R1000.Disassembly)
'''

import os
import sys
import subprocess

R1000DISASS = os.environ.get("AUTOARCHAEOLOGIST_R1000DISASS")
if not R1000DISASS or not os.path.isdir(R1000DISASS):
    R1000DISASS = str(os.environ.get("HOME")) + "/R1000.Disassembly/"
if not R1000DISASS or not os.path.isdir(R1000DISASS):
    R1000DISASS = str(os.environ.get("HOME")) + "/Proj/R1000.Disassembly/"
if not R1000DISASS or not os.path.isdir(R1000DISASS):
    R1000DISASS = None

class R1kExperiment():
    ''' Diagnostic Experiments '''

    def __init__(self, this):
        if R1000DISASS is None:
            return
        dothis = False
        for t in (
           "M32",
           "TYP",
           "VAL",
           "SEQ",
           "IOC",
           "FIU",
           "MEM",
        ):
            if this.has_type(t):
                dothis = True
                break
        if not dothis:
            return

        tf1 = this.tmpfile_for()
        this.writetofile(open(tf1.filename, "wb"))

        tf2 = this.add_utf8_interpretation("Disassembly")
        sys.stdout.flush()
        sys.stderr.flush()

        path = os.path.join(R1000DISASS, "EXP", "disass_experiment.py")

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
            print("    Path:", path)
            print("    Error:", err)
