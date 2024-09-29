'''
GIER Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf

from autoarchaeologist.regnecentralen import gier_text
from autoarchaeologist.generic import samesame
from autoarchaeologist.generic import textfiles
from autoarchaeologist.base import type_case

class DaskTegn(textfiles.TextFile):
    ''' Everything is credible '''

    def credible(self):
        return True

class DaskTc(type_case.TypeCase):
    ''' DASK character set '''

    def __init__(self):
        super().__init__("DASK")
        for i in range(16):
            self.set_slug(0x01 | (i<<1), "%x" % i, "%x" % i)

        self.set_slug(0x00, " ", "«nul»")
        self.set_slug(0x02, " ", "\n")
        self.set_slug(0x04, " ", " ")
        self.set_slug(0x06, " ", "\t")
        self.set_slug(0x08, "-", "-")
        self.set_slug(0x0a, "+", "+")
        self.set_slug(0x0c, "_", "_")
        self.set_slug(0x0e, ".", ".")
        self.set_slug(0x10, "*", "*")
        self.set_slug(0x1e, " ", "«stop»")

class DASK(ddhf.DDHF_Excavation):

    ''' All DASK artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = DaskTc()

        self.add_examiner(gier_text.GIER_Text)
        self.add_examiner(samesame.SameSame)
        self.add_examiner(DaskTegn)

        self.from_bitstore(
            "DASK/SW",
        )

if __name__ == "__main__":
    ddhf.main(
        DASK,
        html_subdir="dask",
        ddhf_topic = "RegneCentralen DASK Computer",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/DASK',
    )
