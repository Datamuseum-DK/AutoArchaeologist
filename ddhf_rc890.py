'''
   Regnecentralen RC890 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class DDHF_Rc890(ddhf.DDHF_Excavation):

    ''' All RC890 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.from_bitstore(
            "RC/RC890",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Rc890,
        html_subdir="rc890",
        ddhf_topic = 'RegneCentralen RC890',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC890'
    )
