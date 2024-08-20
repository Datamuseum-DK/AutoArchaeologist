'''
   Regnecentralen RC4000/RC8000/RC9000 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.base import type_case

from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import samesame
from autoarchaeologist.regnecentralen import rc489k_tape
from autoarchaeologist.regnecentralen import rcsl

class TypeCase(type_case.DS2089):
    ''' RC489k characterset for most artifacts '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x00, ' ', '')
        self.set_slug(0x08, ' ', '«bs»')
        self.set_slug(0x18, ' ', '«can»')
        self.set_slug(0x19, ' ', '«em»', self.EOF)

myTypeCase = TypeCase()

class TextFile(textfiles.TextFile):
    ''' General Text-File-Excavator '''

    MAX_TAIL = 1<<16

class Rc489k(ddhf.DDHF_Excavation):

    ''' All RC4000, RC8000 and RC9000 artifacts '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = myTypeCase

        self.add_examiner(rc489k_tape.Rc489kSaveTapeFile)
        self.add_examiner(rc489k_tape.Rc489kDumpTapeFile)
        self.add_examiner(rc489k_tape.Rc489kTape)
        self.add_examiner(rcsl.RCSL)
        self.add_examiner(TextFile)
        self.add_examiner(samesame.SameSame)

        self.from_bitstore(
            "RC/RC8000/DISK",
            "RC/RC8000/PAPERTAPE",
            "RC/RC8000/TAPE",
            "RC/RC4000/SW",
            "RC/RC4000/TEST",
            "RC/RC9000",
        )

if __name__ == "__main__":
    ddhf.main(
        Rc489k,
        html_subdir="rc489k",
        ddhf_topic = "RC4000/8000/9000",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC4000,_RC8000_and_RC9000',
	downloads=True,
    )
