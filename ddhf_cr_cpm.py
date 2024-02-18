'''
   Christian Rovsing CP/M Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class DDHF_CrCpm(ddhf.DDHF_Excavation):

    ''' All CR8 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(Cpm, **kwargs)

        self.from_bitstore(
            "CR/CR7",
            "CR/CR8",
            "CR/CR16",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_CrCpm,
        html_subdir="cr_cpm",
        ddhf_topic = 'Christian Rovsing CR7, CR8 & CR16 CP/M',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Christian_Rovsing_A/S'
    )
