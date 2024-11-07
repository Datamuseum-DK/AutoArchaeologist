'''
Rational R1000/400 Tapes from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf

from autoarchaeologist.generic.ansi_tape_labels import AnsiTapeLabels
from autoarchaeologist.vendor.rational import r1k_archive
from autoarchaeologist.vendor.rational.r1k_assy import R1kAssyFile
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.os.unix.compress import Compress
from autoarchaeologist.os.unix.tar_file import TarFile
from autoarchaeologist.generic import textfiles

class R1K(ddhf.DDHF_Excavation):

    '''
    Rational R1000/400 tapes except DFS and backup tapes
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.download_limit = 28922073 + 1
        self.add_examiner(AnsiTapeLabels)
        self.add_examiner(r1k_archive.R1K_Archive)
        self.add_examiner(R1kAssyFile)
        self.add_examiner(Compress)
        self.add_examiner(TarFile)
        self.add_examiner(textfiles.TextFile)
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
            #"30000747",
        )

if __name__ == "__main__":
    ddhf.main(
        R1K,
        html_subdir="r1k_tapes",
        ddhf_topic = "Rational R1000/400 Tapes",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
