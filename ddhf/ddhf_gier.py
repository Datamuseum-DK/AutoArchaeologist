'''
GIER Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.vendor.regnecentralen import gier_text
from autoarchaeologist.generic import samesame

import ddhf

class GIER(ddhf.DDHF_Excavation):

    ''' All GIER artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(gier_text.GIER_Text)
        self.add_examiner(samesame.SameSame)

        self.from_bitstore(
            "GIER/ALGOL_4",
            "GIER/ALGOL_II",
            "GIER/ALGOL_III",
            "GIER/ASTRONOMY",
            "GIER/CHEMISTRY",
            "GIER/DEMO",
            "GIER/GAMES",
            "GIER/HELP",
            "GIER/HELP3",
            "GIER/MATHEMATICS",
            "GIER/MISC",
            "GIER/MUSIC",
            "GIER/OTHER_SCIENCE",
            "GIER/TEST",
            "GIER/UTIL",
        )

if __name__ == "__main__":
    ddhf.main(
        GIER,
        html_subdir="gier",
        ddhf_topic = "RegneCentralen GIER Computer",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/GIER',
    )
