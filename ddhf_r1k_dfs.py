'''
   Rational R1000/400 DFS Artifacts from Datamuseum.dk's BitStore
'''

import os
import cProfile

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.generic.samesame import SameSame
import autoarchaeologist.generic.ascii as ascii
from autoarchaeologist.generic.tap_file import TAPfile

from autoarchaeologist.rational.dfs_tape import R1K_DFS_Tape

from autoarchaeologist.ddhf.bitstore import FromBitStore

ascii.CHARSET[0][0] = 16

def R1K_DFS_job(html_dir, **kwargs):

    ctx = DDHF_Excavation(
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )

    ctx.add_examiner(TAPfile)
    ctx.add_examiner(R1K_DFS_Tape)
    ctx.add_examiner(ascii.Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30000750",
        "30000528",
        "30000744",
        "30000407",
        "30000743",
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
    subr_main.main(R1K_DFS_job, "r1k_dfs")
