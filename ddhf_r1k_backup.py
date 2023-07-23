'''
Rational R1000/400 Backup tape from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ansi_tape_labels import AnsiTapeLabels
from autoarchaeologist.rational.r1k_backup import R1kBackup
from autoarchaeologist.rational.r1k_e3_objects import R1kE3Objects
from autoarchaeologist.rational.r1k_assy import R1kAssyFile
from autoarchaeologist.rational.r1k_6zero import R1k6ZeroSegment
from autoarchaeologist.rational.r1k_seg_heap import R1kSegHeap
from autoarchaeologist.generic.ascii import Ascii,CHARSET
from autoarchaeologist.generic.textfiles import TextFiles
from autoarchaeologist.generic.samesame import SameSame

CHARSET[0][0] = 16

class R1KBACKUP(DDHF_Excavation):

    ''' Rational R1000/400 Backup tape '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        self.add_examiner(TAPfile)
        self.add_examiner(AnsiTapeLabels)
        self.add_examiner(R1kBackup)

        self.add_examiner(R1kE3Objects)
        self.add_examiner(R1kAssyFile)
        self.add_examiner(R1k6ZeroSegment)

        self.add_examiner(R1kSegHeap)

        self.add_examiner(Ascii)
        self.add_examiner(TextFiles)
        self.add_examiner(SameSame)

        self.from_bitstore(
            "30000544",	# PAM arrival backup
        )

if __name__ == "__main__":
    main(
        R1KBACKUP,
        html_subdir="r1k_backup",
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
