'''
Rational R1000/400 Backup tape from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ansi_tape_labels import AnsiTapeLabels
from autoarchaeologist.rational.r1k_backup import R1kBackup
from autoarchaeologist.rational.r1k_e3_objects import R1kE3Objects
#from autoarchaeologist.rational.r1k_97seg import R1k97Seg
from autoarchaeologist.rational.r1k_assy import R1K_Assy_File
from autoarchaeologist.rational.r1k_6zero import R1k6ZeroSegment
#from autoarchaeologist.rational.r1k_defaultseg import R1kDefaultSegment
from autoarchaeologist.rational.r1k_seg_heap import R1kSegHeap
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.textfiles import TextFiles
from autoarchaeologist.generic.samesame import SameSame

def r1k_backup_job(**kwargs):

    ''' Rational R1000/400 Backup tape '''

    ctx = DDHF_Excavation(
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
	hexdump_limit=1<<10,
        **kwargs,
    )

    ctx.add_examiner(TAPfile)
    ctx.add_examiner(AnsiTapeLabels)
    ctx.add_examiner(R1kBackup)
    ctx.add_examiner(R1kE3Objects)
    # ctx.add_examiner(R1k97Seg)
    ctx.add_examiner(R1K_Assy_File)
    ctx.add_examiner(R1kSegHeap)
    ctx.add_examiner(R1k6ZeroSegment)
    #ctx.add_examiner(R1kDefaultSegment)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(TextFiles)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30000544",	# PAM arrival backup
    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(r1k_backup_job, subdir="r1k_backup2", downloads=True)
