'''
   Rational R1000 Diagnostic Experiment Files
   ------------------------------------------

   Call out to R1000.Disassembly for disassembling assistance

   (https://github.com/Datamuseum-DK/R1000.Disassembly)
'''

import autoarchaeologist.rational.r1k_disass as r1k_disass

class R1kExperiment():
    ''' Diagnostic Experiments '''

    def __init__(self, this):
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

        r1k_disass.R1kDisass(
            this,
            "EXP/disass_experiment.py",
        )
