'''
Rational R1000/400 Artifacts from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ansi_tape_labels import AnsiTapeLabels
from autoarchaeologist.rational.tape_blocks import R1K_Tape_blocks
from autoarchaeologist.rational.index_data import R1K_Index_Data
from autoarchaeologist.rational.r1k_assy import R1kAssyFile
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.samesame import SameSame

def r1k_job(**kwargs):

    '''
    Rational R1000/400 tapes except DFS and backup tapes
    '''

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
    ctx.add_examiner(R1kAssyFile)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
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

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(r1k_job, subdir="r1k")
