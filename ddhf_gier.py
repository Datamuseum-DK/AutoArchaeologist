'''
	GIER Artifacts from Datamuseum.dk's BitStore
'''

import os

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.regnecentralen.papertapechecksum import RC_PaperTapeCheckSum
from autoarchaeologist.regnecentralen.gier_text import GIER_Text
from autoarchaeologist.ddhf.bitstore import FromBitStore

def GIER_job(html_dir, **kwargs):

    ctx = DDHF_Excavation(
        ddhf_topic = "RegneCentralen GIER Computer",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/GIER'
    )

    ctx.add_examiner(GIER_Text)
    ctx.add_examiner(RC_PaperTapeCheckSum)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "GIER/ALGOL_4",
        "GIER/ALGOL_II",
        "GIER/ALGOL_III",
        "GIER/ASTRONOMY",
        "GIER/CHEMISTRY",
        "GIER/DEMO",
        "GIER/GAMES",
        "GIER/HELP",
        "GIER/HELP3",
        "GIER/MATHEMATICS",
        "GIER/MISC",
        "GIER/MUSIC",
        "GIER/OTHER_SCIENCE",
        "GIER/TEST",
        "GIER/UTIL",
    )

    ctx.start_examination()

    try:
        os.mkdir(html_dir)
    except FileExistsError:
        pass

    ctx.produce_html(
       html_dir=html_dir,
       hexdump_limit=1<<10,
       **kwargs,
    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(GIER_job, "gier")
