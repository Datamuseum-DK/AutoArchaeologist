'''
'''

import os
import sys
import glob

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main
from autoarchaeologist.christianrovsing import cr80_sysone 
from autoarchaeologist.christianrovsing import cr80_fs2 
from autoarchaeologist.intel import isis 
from autoarchaeologist.generic import textfiles 
from autoarchaeologist.zilog.mcz import MCZRIO

class Cr80Floppy(DDHF_Excavation):

    ''' CR80 Floppy disk images'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(cr80_sysone.Cr80SystemOneInterleave)
        self.add_examiner(cr80_sysone.Cr80SystemOneFs)
        self.add_examiner(cr80_fs2.CR80_FS2Interleave)
        self.add_examiner(cr80_fs2.CR80_FS2)
        self.add_examiner(isis.IntelIsis)
        self.add_examiner(MCZRIO)
        self.add_examiner(textfiles.TextFile)

        self.from_bitstore(
            "CR/CR80/SW",
        )

        if True:
            for fn in sorted(glob.glob("/tmp/_*crfd????.bin")):
                b = open(fn, "rb").read()
                if 0 and not load_filter(b):
                    continue
                try:
                    self.add_file_artifact(fn)
                except Exception as err:
                    print("ERR", fn, err)
                    continue


if __name__ == "__main__":
    main(
        Cr80Floppy,
        html_subdir="cr80",
        ddhf_topic = "CR80 Floppy Disks",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
        hexdump_limit=1<<15,
    )
