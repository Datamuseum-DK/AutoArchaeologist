from autoarchaeologist.base.excavation import Excavation
from autoarchaeologist.generic.bigtext import BigText
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum


class ShowcaseExcacation(Excavation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(BigText)
        self.add_examiner(AbsBin)
        self.add_examiner(DGC_PaperTapeCheckSum)
        self.add_examiner(SameSame)
