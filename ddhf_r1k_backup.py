'''
   Rational R1000/400 Backup tape from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf

from autoarchaeologist.generic import ansi_tape_labels
from autoarchaeologist.rational.r1k_backup import R1kBackup
from autoarchaeologist.rational.r1k_e3_objects import R1kE3Objects
from autoarchaeologist.rational.r1k_assy import R1kAssyFile
from autoarchaeologist.rational.r1k_6zero import R1k6ZeroSegment
from autoarchaeologist.rational.r1k_seg_heap import R1kSegHeap
from autoarchaeologist.base import excavation
from autoarchaeologist.base import type_case
from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic.samesame import SameSame

class TextFile(textfiles.TextFile):
    ''' Custom credibility '''

    VERBOSE = True

    def credible(self):
        if len(self.txt) < 5:
            return False
        if len(self.txt) < 10 and '\n' not in self.txt:
            return False
        if len(self.this) - len(self.txt) >= 1024:
            return False
        return True

class TypeCase(type_case.Ascii):
    ''' ... '''

    def __init__(self):
        super().__init__()
        self.set_slug(0, ' ', '«nul»', self.EOF)

class R1kBackup(excavation.Excavation):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = TypeCase()

        self.add_examiner(ansi_tape_labels.AnsiTapeLabels)
        self.add_examiner(R1kBackup)

        self.add_examiner(R1kE3Objects)
        self.add_examiner(R1kAssyFile)
        self.add_examiner(R1k6ZeroSegment)

        self.add_examiner(R1kSegHeap)

        self.add_examiner(TextFile)
        self.add_examiner(SameSame)

class DDHF_R1KBACKUP(ddhf.DDHF_Excavation):

    ''' Rational R1000/400 Backup tape '''

    def __init__(self, **kwargs):
        super().__init__(R1kBackup, **kwargs)

        self.from_bitstore(
            "30000544",	# PAM arrival backup
        )

if __name__ == "__main__":
    ddhf.main(
        R1kBackup,
        html_subdir="r1k_backup",
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
