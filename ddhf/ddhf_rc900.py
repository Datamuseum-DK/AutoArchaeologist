#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
Regnecentralen RC900
~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.base import type_case

from autoarchaeologist.os.unix import unix_fs
from autoarchaeologist.os.unix import compress
from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import samesame

import ddhf

class Rc900FsParams(unix_fs.UnixFsParams):

    BLOCK_SIZES = (1024, )
    POSSIBLE_BYTE_ORDERS = ((2, 1, 0),)
    CLASSES = (unix_fs.UnixFsLittleEndian,)

class RC900(ddhf.DDHF_Excavation):

    '''
    Two CBM900 hard-disk images, one also contains the four distribution
    floppy images.
    '''

    UNIX_FS_PARAMS = Rc900FsParams()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = type_case.WellKnown("iso8859-1")

        self.add_examiner(unix_fs.FindUnixFs)
        self.add_examiner(compress.Compress)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)

        self.from_bitstore(
            "RC/RC900",
        )

if __name__ == "__main__":
    ddhf.main(
        RC900,
        html_subdir="rc900",
        ddhf_topic = "Regnecentalen RC-900",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC900',
    )
