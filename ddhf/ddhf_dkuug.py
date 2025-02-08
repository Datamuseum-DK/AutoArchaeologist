#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   DKUUG and EUUG Conference tapes
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import samesame
from autoarchaeologist.os.unix import tar_file
from autoarchaeologist.os.unix import compress

import ddhf

class DkuugEuug(ddhf.DDHFExcavation):

    '''
    DKUUG and EUUG Conference tapes
    '''

    BITSTORE = (
        "DKUUG",
        "DKUUG/EUUG",
    )

    MEDIA_TYPES = (
        '½" Magnetic Tape',
        '¼" cartridge magtape',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(compress.Compress)
        self.add_examiner(tar_file.TarFile)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)


if __name__ == "__main__":
    ddhf.main(
        DkuugEuug,
        html_subdir="dkuug",
        ddhf_topic = "DKUUG/EUUG Conference tapes",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/DKUUG',
    )
