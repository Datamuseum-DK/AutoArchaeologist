'''
   Rational R1000 Diag Processor Firmware
   --------------------------------------

   Call out to R1000.Disassembly for disassembling assistance

   (https://github.com/Datamuseum-DK/R1000.Disassembly)
'''

from . import r1k_disass

class R1kDiagFirmWare():
    ''' Diag Processor Firmware  '''

    def __init__(self, this):
        r1k_disass.R1kDisass(
            this,
            "EXP/disass_diproc.py",
        )
