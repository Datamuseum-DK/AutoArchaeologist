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
import ddhf.cpm_exc

class Cpm(ddhf.DDHFExcavation):

    ''' All Cpm artifacts '''

    BITSTORE = (
        "-30002875", # PASCAL
        "-30003268", # Ligner CP/M men med COMAL-80 navne semantik
        "-30003296", # Ikke CP/M format
        "RC/RC700",
        "RC/RC750",
        "RC/RC759",
        "RC/RC850/CPM",
        "RC/RC890",
        "CR/CR7",
        "CR/CR8",
        "CR/CR16",
        "JET80",
        "COMPANY/ICL/COMET",
        "COMPANY/BOGIKA",
    )

    MEDIA_TYPES = (
        '5¼" Floppy Disk',
        '8" Floppy Disk',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ddhf.cpm_exc.std_cpm_excavation(self)

if __name__ == "__main__":
    ddhf.main(
        Cpm,
        html_subdir="cpm",
        ddhf_topic = 'CP/M',
        ddhf_topic_link = 'https://datamuseum.dk/wiki'
    )
