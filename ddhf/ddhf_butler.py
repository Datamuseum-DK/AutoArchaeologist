'''
   ICL Butler Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf import cpm_exc

class Butler(ddhf.DDHF_Excavation):
    ''' All Butler artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        cpm_exc.std_cpm_excavation(self)

        self.from_bitstore(
            "COMPANY/BOGIKA",
        )

if __name__ == "__main__":
    ddhf.main(
        Butler,
        html_subdir="butler",
        ddhf_topic = 'Bogika Butler',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/BDS_Butler'
    )
