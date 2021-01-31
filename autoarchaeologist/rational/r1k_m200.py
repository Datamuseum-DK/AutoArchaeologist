'''
   Rational R1000 M200 68K20 Binary Files
   --------------------------------------

   Call out to PyReveng3 for disassembling assistance

   (https://github.com/bsdphk/PyReveng3)
'''

import sys
import subprocess

import autoarchaeologist.generic.pyreveng3 as pyreveng3

class R1kM200File(pyreveng3.PyReveng3):
    ''' IOC program '''

    def __init__(self, this):
        if not this.has_type("M200"):
            return
        sig = this[:6].tobytes().hex()
        if sig == "000400000002":
            super().__init__(
                this,
                "examples/R1000_400/example_m200.py"
            )
        elif sig == "000200000001":
            super().__init__(
                this,
                "examples/R1000_400/example_ioc_fs.py"
            )
        elif sig == "0000fc000000":
            super().__init__(
                this,
                "examples/R1000_400/example_ioc_kernel.py"
            )
