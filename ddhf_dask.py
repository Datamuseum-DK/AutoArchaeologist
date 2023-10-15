'''
GIER Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist.regnecentralen.gier_text import GIER_Text
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic.textfiles import TextFile
from autoarchaeologist import type_case

TextFile.VERBOSE = True

class DaskTegn(TextFile):

    def credible(self):
        return True

class DASK_TC(type_case.TypeCase):

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

class DASK(DDHF_Excavation):

    ''' All DASK artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(GIER_Text)
        self.add_examiner(SameSame)
        self.add_examiner(DaskTegn)

        self.type_case = DASK_TC()

        self.from_bitstore(
            "DASK/SW",
        )

if __name__ == "__main__":
    main(
        DASK,
        html_subdir="dask",
        ddhf_topic = "RegneCentralen DASK Computer",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/DASK',
    )
