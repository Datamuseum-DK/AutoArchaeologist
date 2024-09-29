'''
   Regnecentralen RC700 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class Rc700(ddhf.DDHF_Excavation):

    ''' All RC700 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ddhf.cpm_exc.std_cpm_excavation(self)

        self.from_bitstore(
            "-30003268", # Ligner CP/M men med COMAL-80 navne semantik
            "-30003296", # Ikke CP/M format
            "RC/RC700",
        )

if __name__ == "__main__":
    ddhf.main(
        Rc700,
        html_subdir="rc700",
        ddhf_topic = 'RegneCentralen RC700 "Piccolo"',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC700_Piccolo'
    )
