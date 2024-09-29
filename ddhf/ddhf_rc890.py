'''
   Regnecentralen RC890 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class Rc890(ddhf.DDHF_Excavation):

    ''' All RC890 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        cpm_exc.std_cpm_excavation(self)

        self.from_bitstore(
            "RC/RC890",
        )

if __name__ == "__main__":
    ddhf.main(
        Rc890,
        html_subdir="rc890",
        ddhf_topic = 'RegneCentralen RC890',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC890'
    )
