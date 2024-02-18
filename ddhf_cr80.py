'''
Christian Rovsing A/S CR80 Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf

from autoarchaeologist.base import excavation
from autoarchaeologist.christianrovsing import cr80_sysone
from autoarchaeologist.christianrovsing import cr80_fs2
from autoarchaeologist.intel import isis
from autoarchaeologist.generic import textfiles
from autoarchaeologist.zilog import mcz

class Cr80Floppy(excavation.Excavation):
    ''' CR80 Floppy disk images'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(cr80_sysone.Cr80SystemOneInterleave)
        self.add_examiner(cr80_sysone.Cr80SystemOneFs)
        self.add_examiner(cr80_fs2.CR80_FS2Interleave)
        self.add_examiner(cr80_fs2.CR80_FS2)
        self.add_examiner(isis.IntelIsis)
        self.add_examiner(mcz.MCZRIO)
        self.add_examiner(textfiles.TextFile)


class DDHF_Cr80Floppy(ddhf.DDHF_Excavation):

    ''' CR80 Floppy disk images'''

    def __init__(self, **kwargs):
        super().__init__(Cr80Floppy, **kwargs)

        self.from_bitstore(
            "CR/CR80/SW",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Cr80Floppy,
        html_subdir="cr80",
        ddhf_topic = "CR80 Hard and Floppy Disks",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
    )
