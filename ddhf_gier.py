'''
GIER Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist.regnecentralen.gier_text import GIER_Text
from autoarchaeologist.generic.samesame import SameSame

class GIER(DDHF_Excavation):

    ''' All GIER artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(GIER_Text)
        self.add_examiner(SameSame)

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
    main(
        GIER,
        html_subdir="gier",
        ddhf_topic = "RegneCentralen GIER Computer",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/GIER',
    )
