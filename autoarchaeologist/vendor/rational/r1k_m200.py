#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   R1000 M200 68K20 Binary Files
   =============================

   Call out to PyReveng3 for disassembling assistance

   (https://github.com/bsdphk/PyReveng3)
'''

from . import r1k_disass

class R1kM200File():
    ''' IOC program '''

    def __init__(self, this):
        if len(this) <= 1024 and b'Unknown boot device type' in this.tobytes():
            r1k_disass.R1kDisass(
                this,
                "DFS/disass_dfs.py",
            )
        elif this.has_type("M200"):
            sig = this[:4].tobytes().hex()
            if sig == "00040000":
                this.add_note("M200_PROGRAM")
                r1k_disass.R1kDisass(
                    this,
                    "DFS/disass_dfs.py",
                )
            elif sig == "00020000":
                this.add_note("M200_FS")
                r1k_disass.R1kDisass(
                    this,
                    "DFS/disass_dfs.py",
                )
            elif sig == "0000fc00":
                this.add_note("M200_KERNEL")
                r1k_disass.R1kDisass(
                    this,
                    "DFS/disass_dfs.py",
                )
            else:
                print(this, "Unidentified .M200")
        elif this.has_type("M200_PROM"):
            i = this[:0x400].tobytes()
            if b'S3F5000700' in i:
                this.add_note("M200_PROM_RESHA")
                r1k_disass.R1kDisass(
                    this,
                    "DFS/disass_dfs.py",
                )
            elif b'S3F5800' in i:
                this.add_note("M200_PROM_IOC")
                r1k_disass.R1kDisass(
                    this,
                    "DFS/disass_dfs.py",
                )
            else:
                print(this, "Unidentified .M200_PROM")
        elif this.has_type("M400_PROM"):
            i = this[:0x400].tobytes()
            if b'S3F5000700' in i:
                this.add_note("M400_PROM_RESHA")
                r1k_disass.R1kDisass(
                    this,
                    "DFS/disass_dfs.py",
                )
            elif b'S3F5800' in i:
                this.add_note("M400_PROM_IOC")
                r1k_disass.R1kDisass(
                    this,
                    "DFS/disass_dfs.py",
                )
            else:
                print(this, "Unidentified .M400_PROM")
