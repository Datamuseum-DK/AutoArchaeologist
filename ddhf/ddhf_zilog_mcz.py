'''
   Zilog MCZ/1 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf

from autoarchaeologist.vendor.zilog import mcz
from autoarchaeologist.vendor.zilog import zdos_basic
from autoarchaeologist.generic import textfiles

class ZilogMCZ(ddhf.DDHF_Excavation):

    ''' Zilog MCZ Floppy Disks '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(mcz.MCZRIO)
        self.add_examiner(zdos_basic.ZdosBasic)
        self.add_examiner(textfiles.TextFile)

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
