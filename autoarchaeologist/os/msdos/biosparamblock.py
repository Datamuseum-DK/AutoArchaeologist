#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Microsoft Bios Parameter Block
   ==============================
'''

import collections

from ...base import octetview as ov

Geometry = collections.namedtuple(
    "Geometry",
    "cyl hd sect bps rsv nfat spcl rdir nfsc tsect",
)

class BiosParamBlock(ov.Struct):
    ''' ... '''

    # Field names mirro FreeBSD's msdosfs
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,

            bsJmp_=3,
            bsOem_=ov.Text(8),

            # From DOS2.0
            bsBytesPerSec_=ov.Le16,
            bsSectPerClust_=ov.Octet,
            bsResSectors_=ov.Le16,
            bsFATS_=ov.Octet,
            bsRootDirEnts_=ov.Le16,
            bsSectors_=ov.Le16,
            bsMedia_=ov.Octet,
            bsFATsecs_=ov.Le16,

            # From DOS3.0
            bsSectPerTrack_=ov.Le16,
            bsHeads_=ov.Le16,
            bsHiddenSecs_=ov.Le32,

            # From DOS3.2
            bpbHugeSectors_=ov.Le32, # DOS3.2: Le16, DOS3.31: Le32
            more=True,
        )
        if tree.this[lo + 0x26] in (0x28, 0x29):
            # From OS/2 1.0, DOS 4.0
            self.add_field("bsPhysDrive", ov.Octet)
            self.add_field("bsReserved", ov.Octet)
            self.add_field("bsExtBootSig", ov.Octet)
            self.add_field("bsVolId", ov.Le32)
            self.add_field("bsVolName", ov.Text(11))
            self.add_field("bsFsType", ov.Text(8))
        elif ov.Le32(tree, 0x24).val > 0x200000:
            # Seen om Concurrent DOS hard disk
            self.add_field("bsPhysDrive", ov.Octet)
            self.add_field("bsReserved", ov.Octet)
            self.add_field("bsExtBootSig", ov.Octet)
            self.add_field("bsUnknown", 11)
            self.add_field("bsVolName", ov.Text(12))
        else:
            self.add_field("bsBigFATsecs", ov.Le32)
            self.add_field("bsExtFlags", ov.Le16)
            self.add_field("bsFsInfo", ov.Le16)
            self.add_field("bsRootClust", ov.Le32)
            self.add_field("bsFSVers", ov.Le16)
            self.add_field("bsBackup", ov.Le16)
            self.add_field("bsReserved", ov.Text(12))

        self.done()
        if self.is_sane():
            if self.bsSectors.val:
                tsect = self.bsSectors.val
            else:
                tsect = self.bpbHugeSectors.val
            self.geom = Geometry(
                tsect // (self.bsHeads.val * self.bsSectPerTrack.val),
                self.bsHeads.val,
                self.bsSectPerTrack.val,
                self.bsBytesPerSec.val,
                self.bsResSectors.val,
                self.bsFATS.val,
                self.bsSectPerClust.val,
                self.bsRootDirEnts.val,
                self.bsFATsecs.val,
                tsect,
            )
        else:
            self.geom = None

    def is_sane(self):
        ''' Sanity check '''

        if not self.bsBytesPerSec.val in (128, 256, 512, 1024, 2048, 4096):
            # Improbable sector size
            return False
        if self.bsResSectors.val == 0:
            # BPB and FAT cannot overlap
            return False
        return True
