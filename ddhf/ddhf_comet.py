'''
   ICL Comet Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class Comet(ddhf.DDHF_Excavation):

    ''' All Comet artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ddhf.cpm_exc.std_cpm_excavation(self)

        self.from_bitstore(
            "COMPANY/ICL/COMET",
        )

if __name__ == "__main__":
    ddhf.main(
        Comet,
        html_subdir="comet",
        ddhf_topic = 'ICL Comet',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/ICL_Comet'
    )
