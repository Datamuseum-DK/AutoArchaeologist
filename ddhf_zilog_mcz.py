'''
   Zilog MCZ/1 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf

from autoarchaeologist.zilog import mcz
from autoarchaeologist.generic import textfiles
from autoarchaeologist.base import excavation

class ZilogMCZ(excavation.Excavation):

    ''' Zilog MCZ Floppy Disks '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(mcz.MCZRIO)
        self.add_examiner(textfiles.TextFile)

class DDHF_ZilogMCZ(ddhf.DDHF_Excavation):
    def __init__(self, **kwargs):
        super().__init__(ZilogMCZ, **kwargs)

        self.from_bitstore(
            "COMPANY/ZILOG",
        )

if __name__ == "__main__":
    ddhf.main(
        ZilogMCZ,
        html_subdir="zilog_mcz",
        ddhf_topic = "Zilog MCZ Floppy Disks",
        # ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
    )
