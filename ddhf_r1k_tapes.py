'''
Rational R1000/400 Tapes from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ansi_tape_labels import AnsiTapeLabels
from autoarchaeologist.rational.tape_blocks import R1K_Tape_blocks
from autoarchaeologist.rational.index_data import R1K_Index_Data
from autoarchaeologist.rational.r1k_assy import R1kAssyFile
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.unix.compress import Compress
from autoarchaeologist.unix.tar_file import TarFile

class R1K(DDHF_Excavation):

    '''
    Rational R1000/400 tapes except DFS and backup tapes
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(TAPfile)
        self.add_examiner(AnsiTapeLabels)
        self.add_examiner(R1K_Tape_blocks)
        self.add_examiner(R1K_Index_Data)
        self.add_examiner(R1kAssyFile)
        self.add_examiner(Compress)
        self.add_examiner(TarFile)
        self.add_examiner(Ascii)
        self.add_examiner(SameSame)

        self.from_bitstore(
            "-30000530",	# == 30000409
            "-30000537",	# == 30000405
            "-30000750",	# DFS
            "-30000528",	# DFS
            "-30000744",	# DFS
            "-30000407",	# DFS
            "-30000408",	# PNG
            "-30000743",	# DFS
            "-30000410",	# PNG
            "-30000406",	# PNG
            "-30000746",	# Defects tape
            "-30000533",	# ASIS(AIX)
            "-30000544",	# PAM arrival backup, different format.
            "RATIONAL_1000/TAPE",
            #"30000535",
        )

if __name__ == "__main__":
    main(
        R1K,
        html_subdir="r1k_tapes",
        ddhf_topic = "Rational R1000/400 Tapes",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
