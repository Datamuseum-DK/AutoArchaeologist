#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   (C)CP/M Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
from ddhf import cpm_exc

from autoarchaeologist.vendor.sharp import mz80b

class Cpm(cpm_exc.DdhfExcavationCpm):

    ''' All Cpm artifacts '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_examiner(mz80b.Mz80BFloppies)

    BITSTORE = (
        "-30002875", # PASCAL
        "-30003268", # Ligner CP/M men med COMAL-80 navne semantik
        "-30003296", # Ikke CP/M format
        "RC/RC700",
        "RC/RC750",
        "RC/RC759",
        "RC/RC850/CPM",
        "RC/RC850/SW",
        "RC/RC850",
        "RC/RC890",
        "CR/CR7",
        "CR/CR8",
        "CR/CR16",
        "JET80",
        "COMPANY/ICL/COMET",
        "COMPANY/BOGIKA",
        "COMPANY/SHARP",
    )

    MEDIA_TYPES = (
        '5¼" Floppy Disk',
        '8" Floppy Disk',
    )

if __name__ == "__main__":
    ddhf.main(
        Cpm,
        html_subdir="cpm",
        ddhf_topic = 'CP/M',
        ddhf_topic_link = 'https://datamuseum.dk/wiki'
    )
