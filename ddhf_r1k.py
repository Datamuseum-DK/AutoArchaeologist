'''
   Rational R1000/400 Artifacts from Datamuseum.dk's BitStore
'''

import os
import cProfile

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ansi_tape_labels import Ansi_Tape_labels

from autoarchaeologist.rational.tape_blocks import R1K_Tape_blocks
from autoarchaeologist.rational.index_data import R1K_Index_Data

from autoarchaeologist.ddhf.bitstore import FromBitStore

def R1K_job(html_dir, **kwargs):

    ctx = DDHF_Excavation(
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )

    ctx.add_examiner(TAPfile)
    ctx.add_examiner(Ansi_Tape_labels)
    ctx.add_examiner(R1K_Tape_blocks)
    ctx.add_examiner(R1K_Index_Data)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "-30000530",	# == 30000409
        "-30000537",	# == 30000405
        "-30000750",
        "-30000528",
        "-30000744",
        "-30000407",
        "-30000743",
        "RATIONAL_1000/TAPE",
        #"30000535", 
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
        
    i = R1K_job("/tmp/_aa_r1k", downloads=True)
        
    print("Now point your browser at:")
    print("\t", i.link_prefix + '/' + i.filename_for(i))

