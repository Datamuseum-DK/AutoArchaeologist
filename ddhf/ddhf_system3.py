#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
IBM System/3
~~~~~~~~~~~~
'''

import sys

from autoarchaeologist.base import type_case
from autoarchaeologist.generic import samesame
from autoarchaeologist.container import argv
from autoarchaeologist.vendor.ibm import ga21_9128
from autoarchaeologist.vendor.ibm.midrange import system3

import ddhf

class System3(ddhf.DDHFExcavation):

    ''' IBM System/3 '''

    BITSTORE = (
        "COMPANY/IBM/SYSTEM3",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(ga21_9128.Ga21_9182)
        self.add_examiner(samesame.SameSame)
        self.add_examiner(s3x.S3X)
        self.add_examiner(s3x.S3Y)
        self.add_examiner(s3x.S3Z)

        self.type_case = type_case.WellKnown("cp037")


        for fn in sys.argv[1:]:
            argv.argv_file(self, fn)

if __name__ == "__main__":
    ddhf.main(
        System3,
        html_subdir="system3",
        ddhf_topic = "IBM System/3",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/IBM_System/3',
    )
