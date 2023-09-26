'''
Regnecentralen RC3600/RC7000 Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist import type_case

from autoarchaeologist.regnecentralen.domus_fs import Domus_Filesystem
from autoarchaeologist.regnecentralen.rc3600_fdtape import RC3600_FD_Tape
from autoarchaeologist.regnecentralen.rc7000_comal import ComalSaveFile
from autoarchaeologist.generic.bigdigits import BigDigits
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.relbin import RelBin
from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum
from autoarchaeologist.regnecentralen.rcsl import RCSL
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic import textfiles

class TxtFile(textfiles.TextFile):
    VERBOSE=False
    MAX_TAIL=512

class Domus_DS2089(type_case.DS2089):
    ''' ... '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x00, ' ', '«nul»', self.EOF)
        self.set_slug(0x0c, ' ', '«ff»\n')
        self.set_slug(0x0d, ' ', '')
        self.set_slug(0x7f, ' ', '')

class EvenTextFile(textfiles.TextFile):
    VERBOSE=False
    MAX_TAIL=512
    TYPE_CASE = type_case.EvenPar(Domus_DS2089())

class OddTextFile(textfiles.TextFile):
    VERBOSE=False
    MAX_TAIL=512
    TYPE_CASE = type_case.OddPar(Domus_DS2089())

class Rc3600(DDHF_Excavation):

    ''' All RC3600 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = Domus_DS2089()

        self.add_examiner(Domus_Filesystem)
        self.add_examiner(RC3600_FD_Tape)
        self.add_examiner(ComalSaveFile)
        self.add_examiner(AbsBin)
        self.add_examiner(RelBin)
        self.add_examiner(BigDigits)
        self.add_examiner(DGC_PaperTapeCheckSum)
        self.add_examiner(RCSL)
        self.add_examiner(TxtFile)
        self.add_examiner(EvenTextFile)
        self.add_examiner(OddTextFile)
        self.add_examiner(SameSame)

        self.from_bitstore(
            #"RC/RC3600/COMAL",
            #"RC/RC3600/DE2",
            #"RC/RC3600/DISK",
            "RC/RC3600/DOMUS",
            "RC/RC3600/HW",
            "RC/RC3600/LOADER",
            "RC/RC3600/MUSIL",
            #"RC/RC3600/PAPERTAPE",
            #"RC/RC3600/SW",
            #"RC/RC3600/TEST",
            #"RC/RC3600/UTIL",
        )

if __name__ == "__main__":
    main(
        Rc3600,
        html_subdir="rc3600",
        ddhf_topic = "RegneCentralen RC3600/RC7000",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC/RC7000',
    )
