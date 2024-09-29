'''
   ICL Butler Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class Butler(ddhf.DDHF_Excavation):
    ''' All Butler artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ddhf.cpm_exc.std_cpm_excavation(self)

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
