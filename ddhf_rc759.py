'''
   Regnecentralen RC759 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class DDHF_Rc759(ddhf.DDHF_Excavation):

    ''' All RC759 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(Cpm, **kwargs)

        self.from_bitstore(
            "-30002875",
            "RC/RC759",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Rc759,
        html_subdir="rc759",
        ddhf_topic = 'RegneCentralen RC759 "Piccoline"',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC_Piccoline'
    )
