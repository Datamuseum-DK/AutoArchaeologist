'''
   Regnecentralen RC3600/RC7000 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf

from autoarchaeologist.base import type_case

from autoarchaeologist.regnecentralen import domus_fs
from autoarchaeologist.regnecentralen import rc3600_fdtape
from autoarchaeologist.regnecentralen import rc3600_fcopy
from autoarchaeologist.regnecentralen import rc7000_comal
from autoarchaeologist.regnecentralen import rc3600_ldfs
from autoarchaeologist.generic import bigtext
from autoarchaeologist.data_general import absbin
from autoarchaeologist.data_general import relbin
from autoarchaeologist.data_general import papertapechecksum
from autoarchaeologist.regnecentralen import rcsl
from autoarchaeologist.generic import samesame
from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import intel_hex

class DomusDS2089(type_case.DS2089):
    ''' typical use charset '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x00, ' ', '«nul»', self.IGNORE)
        self.set_slug(0x07, ' ', '«bel»')
        self.set_slug(0x0c, ' ', '«ff»\n')
        self.set_slug(0x0d, ' ', '')
        self.set_slug(0x0e, ' ', '«so»')
        self.set_slug(0x0f, ' ', '«si»')
        self.set_slug(0x19, ' ', '«eof»', self.EOF)
        self.set_slug(0x7f, ' ', '')

class TextFile(textfiles.TextFile):
    ''' Non-parity '''

    TYPE_CASE = DomusDS2089()
    MAX_TAIL=512*6

class TextFileEven(textfiles.TextFile):
    ''' Even-parity '''

    TYPE_CASE = type_case.EvenPar(DomusDS2089())
    MAX_TAIL=512*6

class TextFileOdd(textfiles.TextFile):
    ''' Odd-parity '''

    TYPE_CASE = type_case.OddPar(DomusDS2089())
    MAX_TAIL=512*6

class Id7000(ddhf.DDHF_Excavation):

    ''' All ID-7000 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = DomusDS2089()

        self.add_examiner(bigtext.BigText)
        self.add_examiner(samesame.SameSame)
        self.add_examiner(intel_hex.IntelHex)
        self.add_examiner(TextFile)
        self.add_examiner(TextFileEven)
        self.add_examiner(TextFileOdd)

        self.from_bitstore(
            "DDE/ID-7000",
        )

if __name__ == "__main__":
    ddhf.main(
        Id7000,
        html_subdir="id7000",
        ddhf_topic = "DDE ID-7000",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/DDE_ID-7000',
    )
