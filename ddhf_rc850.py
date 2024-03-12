'''
Regnecentralen RC850 Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class DDHF_Rc850(ddhf.DDHF_Excavation):

    ''' All RC850 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(Cpm, **kwargs)

        self.from_bitstore(
            "RC/RC850/CPM",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Rc850,
        html_subdir="rc850",
        ddhf_topic = 'RegneCentralen RC850',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC850'
    )
