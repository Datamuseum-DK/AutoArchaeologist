'''
Jet Computer Jet80 Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class DDHF_Jet80(ddhf.DDHF_Excavation):

    ''' All Jet80 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(Cpm, **kwargs)

        self.from_bitstore(
            "JET80",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Jet80,
        html_subdir="jet80",
        ddhf_topic = 'Jet Computer Jet80',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Jet_Computer_JET-80'
    )
