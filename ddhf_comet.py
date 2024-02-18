'''
   ICL Comet Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class DDHF_Comet(ddhf.DDHF_Excavation):

    ''' All Comet artifacts '''

    def __init__(self, **kwargs):
        super().__init__(Cpm, **kwargs)

        self.from_bitstore(
            "COMPANY/ICL/COMET",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Comet,
        html_subdir="comet",
        ddhf_topic = 'ICL Comet',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/ICL_Comet'
    )
