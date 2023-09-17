'''
Rational R1000/400 DFS Tapes from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ansi_tape_labels import AnsiTapeLabels
from autoarchaeologist.generic.sccs_id import SccsId
from autoarchaeologist.rational.tape_blocks import R1K_Tape_blocks
from autoarchaeologist.rational.index_data import R1K_Index_Data
from autoarchaeologist.rational.dfs_tape import R1K_DFS_Tape
from autoarchaeologist.rational.r1k_assy import R1kAssyFile
from autoarchaeologist.rational.r1k_configuration import R1kM200ConfigFile
from autoarchaeologist.rational.r1k_ucode import R1K_Ucode_File
from autoarchaeologist.rational.r1k_m200 import R1kM200File
from autoarchaeologist.rational.r1k_experiment import R1kExperiment

from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic import textfiles

class R1KDFS(DDHF_Excavation):
    ''' Rational R1000/400 DFS tapes '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(TAPfile)
        self.add_examiner(AnsiTapeLabels)
        self.add_examiner(R1K_Tape_blocks)
        self.add_examiner(R1K_Index_Data)
        self.add_examiner(R1K_DFS_Tape)
        self.add_examiner(R1kM200ConfigFile)
        self.add_examiner(R1kAssyFile)
        self.add_examiner(R1K_Ucode_File)
        self.add_examiner(R1kM200File)
        self.add_examiner(R1kExperiment)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(SccsId)
        self.add_examiner(SameSame)

        self.from_bitstore(
            "30000744",   # precise file sizes
            "30000407",   # precise file sizes

            "30000528",   # file sizes rounded up
            "30000743",   # file sizes rounded up
            "30000750",   # file sizes rounded up
        )

if __name__ == "__main__":
    main(
        R1KDFS,
        html_subdir="r1k_dfs",
        ddhf_topic = "Rational R1000/400 DFS Tapes",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
