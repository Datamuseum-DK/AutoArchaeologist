'''
Rational R1000/400 DFS Artifacts from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ansi_tape_labels import AnsiTapeLabels
from autoarchaeologist.generic.sccs_id import SccsId
from autoarchaeologist.rational.tape_blocks import R1K_Tape_blocks
from autoarchaeologist.rational.index_data import R1K_Index_Data
from autoarchaeologist.rational.dfs_tape import R1K_DFS_Tape
from autoarchaeologist.rational.r1k_assy import R1kAssyFile
from autoarchaeologist.rational.r1k_ucode import R1K_Ucode_File
from autoarchaeologist.rational.r1k_m200 import R1kM200File
from autoarchaeologist.rational.r1k_experiment import R1kExperiment

from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic.ascii import Ascii

def r1k_dfs_job(**kwargs):

    ''' Rational R1000/400 DFS tapes '''

    ctx = DDHF_Excavation(
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
        hexdump_limit=1<<10,
        **kwargs,
    )

    ctx.add_examiner(TAPfile)
    ctx.add_examiner(AnsiTapeLabels)
    ctx.add_examiner(R1K_Tape_blocks)
    ctx.add_examiner(R1K_Index_Data)
    ctx.add_examiner(R1K_DFS_Tape)
    ctx.add_examiner(R1kAssyFile)
    ctx.add_examiner(R1K_Ucode_File)
    ctx.add_examiner(R1kM200File)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(R1kExperiment)
    ctx.add_examiner(SccsId)
    #ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30000744",   # precise file sizes
        "30000407",   # precise file sizes

        "30000528",   # file sizes rounded up
        "30000743",   # file sizes rounded up
        "30000750",   # file sizes rounded up

    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(r1k_dfs_job, subdir="r1k_dfs", downloads=True)
