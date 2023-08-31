'''
'''

import os
import sys

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main
from autoarchaeologist.generic.ascii import Ascii, CHARSET
from autoarchaeologist.intel.isis import Intel_Isis

# CHARSET[0x00][0] |= 4

class Intel_ISIS(DDHF_Excavation):

    ''' Intel ISIS Floppy Disks '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(Intel_Isis)
        self.add_examiner(Ascii)

        self.from_bitstore(
            "COMPANY/INTEL/ISIS",
        )

        for fd in (
            #"crfd0031",
            #"crfd0032",
            #"crfd0033",
            #"crfd0034",
            #"crfd0102",
            #"crfd0103",
            #"crfd0105",
            #"crfd0107",
            #"crfd0109",
        ):
            self.add_file_artifact("/tmp/_" + fd + ".bin")


if __name__ == "__main__":
    main(
        Intel_ISIS,
        html_subdir="Intel_ISIS",
        ddhf_topic = "Intel ISIS Floppy Disks",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
    )
