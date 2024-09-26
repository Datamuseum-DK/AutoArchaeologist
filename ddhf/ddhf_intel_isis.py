'''
Intel ISIS Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf

from autoarchaeologist.intel import isis
from autoarchaeologist.generic import textfiles

class IntelISIS(ddhf.DDHF_Excavation):
    ''' Intel ISIS Floppy Disks '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(isis.IntelIsis)
        self.add_examiner(textfiles.TextFile)

        self.from_bitstore(
            "COMPANY/INTEL/ISIS",
        )

if __name__ == "__main__":
    ddhf.main(
        IntelISIS,
        html_subdir="intel_isis",
        ddhf_topic = "Intel ISIS Floppy Disks",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
    )
