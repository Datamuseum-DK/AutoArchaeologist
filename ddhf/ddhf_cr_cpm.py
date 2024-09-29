'''
   Christian Rovsing CP/M Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class CrCpm(ddhf.DDHF_Excavation):

    ''' All CR8 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ddhf.cpm_exc.std_cpm_excavation(self)

        self.from_bitstore(
            "CR/CR7",
            "CR/CR8",
            "CR/CR16",
        )

if __name__ == "__main__":
    ddhf.main(
        CrCpm,
        html_subdir="cr_cpm",
        ddhf_topic = 'Christian Rovsing CR7, CR8 & CR16 CP/M',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Christian_Rovsing_A/S'
    )
