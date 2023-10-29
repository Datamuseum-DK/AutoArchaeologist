'''
'''

import glob

from autoarchaeologist import ddhf
from autoarchaeologist.christianrovsing import cr80_sysone
from autoarchaeologist.christianrovsing import cr80_fs2
from autoarchaeologist.generic import textfiles

class Cr80SMD(ddhf.DDHF_Excavation):

    ''' CR80 Floppy disk images'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(cr80_sysone.Cr80SystemOneInterleave)
        self.add_examiner(cr80_sysone.Cr80SystemOneFs)
        self.add_examiner(cr80_fs2.CR80_FS2Interleave)
        self.add_examiner(cr80_fs2.CR80_FS2)
        self.add_examiner(textfiles.TextFile)

        if True:
            for fn in sorted(glob.glob("/critter/DDHF/CR80_SMD/_fnj1")):
                b = open(fn, "rb").read()
                try:
                    self.add_file_artifact(fn)
                except Exception as err:
                    print("ERR", fn, err)
                    continue


if __name__ == "__main__":
    ddhf.main(
        Cr80SMD,
        html_subdir="cr80smd",
        ddhf_topic = "CR80 SMD Disks",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
    )
