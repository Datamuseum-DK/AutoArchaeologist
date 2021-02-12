'''
   Rational R1000 M200 68K20 Binary Files
   --------------------------------------

   Call out to PyReveng3 for disassembling assistance

   (https://github.com/bsdphk/PyReveng3)
'''

import autoarchaeologist.generic.pyreveng3 as pyreveng3

class R1kM200File():
    ''' IOC program '''

    def __init__(self, this):
        if len(this) <= 1024 and b'Unknown boot device type' in this.tobytes():
            pyreveng3.PyReveng3(
                this,
                "examples/R1000_400/example_ioc_dfs_bootstrap.py"
            )
        elif this.has_type("M200"):
            sig = this[:6].tobytes().hex()
            if sig == "000400000002":
                this.add_note("M200_PROGRAM")
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_m200.py"
                )
            elif sig == "000200000001":
                this.add_note("M200_FS")
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_fs.py"
                )
            elif sig == "0000fc000000":
                this.add_note("M200_KERNEL")
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_kernel.py"
                )
            else:
                print(this, "Unidentified .M200")
        elif this.has_type("M200_PROM"):
            i = this[:0x400].tobytes()
            if b'S3F5000700' in i:
                this.add_note("M200_PROM_RESHA")
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_resha_eeprom.py"
                )
            elif b'S3F5800' in i:
                this.add_note("M200_PROM_IOC")
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_eeprom_part1.py"
                )
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_eeprom_part2.py"
                )
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_eeprom_part3.py"
                )
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_eeprom_part4.py"
                )
            else:
                print(this, "Unidentified .M200_PROM")
        elif this.has_type("M400_PROM"):
            i = this[:0x400].tobytes()
            if b'S3F5000700' in i:
                this.add_note("M400_PROM_RESHA")
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_resha_eeprom.py"
                )
            elif b'S3F5800' in i:
                this.add_note("M400_PROM_IOC")
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_eeprom_part1.py"
                )
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_eeprom_part2.py"
                )
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_eeprom_part3.py"
                )
                pyreveng3.PyReveng3(
                    this,
                    "examples/R1000_400/example_ioc_eeprom_part4.py"
                )
            else:
                print(this, "Unidentified .M400_PROM")
