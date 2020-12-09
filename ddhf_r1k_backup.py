'''
   Rational R1000/400 Artifacts from Datamuseum.dk's BitStore
'''

import os
import cProfile

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ansi_tape_labels import AnsiTapeLabels

from autoarchaeologist.rational.tape_blocks import R1K_Tape_blocks
from autoarchaeologist.rational.r1k_assy import R1K_Assy_File
from autoarchaeologist.rational.r1k_backup import R1kBackup

from autoarchaeologist.ddhf.bitstore import FromBitStore

def R1K_backup_job(html_dir, **kwargs):

    ctx = DDHF_Excavation(
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )

    ctx.add_examiner(TAPfile)
    ctx.add_examiner(AnsiTapeLabels)
    ctx.add_examiner(R1kBackup)
    ctx.add_examiner(R1K_Assy_File)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30000544",	# PAM arrival backup
    )

    ctx.start_examination()

    try:
        os.mkdir(html_dir)
    except FileExistsError:
        pass

    ctx.produce_html(
       html_dir=html_dir,
       hexdump_limit=1<<10,
       **kwargs
    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(R1K_backup_job, "r1k_backup", downloads=True)
