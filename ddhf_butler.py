'''
   ICL Butler Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf, Excavation
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class DDHF_Butler(ddhf.DDHF_Excavation):
    ''' All Butler artifacts '''

    def __init__(self, **kwargs):
        super().__init__(Cpm, **kwargs)

        self.from_bitstore(
            "COMPANY/BOGIKA",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Butler,
        html_subdir="butler",
        ddhf_topic = 'Bogika Butler',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/BDS_Butler'
    )
