'''
Regnecentralen RC850 Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class Rc850(ddhf.DDHF_Excavation):

    ''' All RC850 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        cpm_exc.std_cpm_excavation(self)

        self.from_bitstore(
            "RC/RC850/CPM",
        )

if __name__ == "__main__":
    ddhf.main(
        Rc850,
        html_subdir="rc850",
        ddhf_topic = 'RegneCentralen RC850',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC850'
    )
