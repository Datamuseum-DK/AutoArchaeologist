'''
'''

import os
import sys
import glob

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main
from autoarchaeologist.christianrovsing import cr80_sysone 
from autoarchaeologist.intel import isis 
from autoarchaeologist.generic import textfiles 

class Cr80Floppy(DDHF_Excavation):

    ''' CR80 Floppy disk images'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(cr80_sysone.Cr80SystemOneInterleave)
        self.add_examiner(cr80_sysone.Cr80SystemOneFs)
        self.add_examiner(isis.IntelIsis)
        self.add_examiner(textfiles.TextFile)

        self.from_bitstore(
            "CR/CR80/SW",
        )

if __name__ == "__main__":
    main(
        Cr80Floppy,
        html_subdir="cr80",
        ddhf_topic = "CR80 Floppy Disks",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
        hexdump_limit=1<<15,
    )
