'''
   Regnecentralen RC700 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class DDHF_Rc700(ddhf.DDHF_Excavation):

    ''' All RC700 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(Cpm, **kwargs)

        self.from_bitstore(
            "-30003268", # Ligner CP/M men med COMAL-80 navne semantik
            "-30003296", # Ikke CP/M format
            "RC/RC700",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Rc700,
        html_subdir="rc700",
        ddhf_topic = 'RegneCentralen RC700 "Piccolo"',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC700_Piccolo'
    )
