
import glob
import os

import autoarchaeologist

from autoarchaeologist.generic.bigdigits import BigDigits
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum
from autoarchaeologist.regnecentralen.papertapechecksum import RC_PaperTapeCheckSum
from autoarchaeologist.regnecentralen.gier_text import GIER_Text
from autoarchaeologist.ddhf.bitstore import FromBitStore


if __name__ == "__main__":


    ctx = autoarchaeologist.Excavation()

    ctx.add_examiner(GIER_Text)
    ctx.add_examiner(BigDigits)
    ctx.add_examiner(DGC_PaperTapeCheckSum)
    ctx.add_examiner(RC_PaperTapeCheckSum)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "GIER/DEMO",
        "GIER/ALGOL_II",
        "GIER/ALGOL_III",
        "GIER/ALGOL_4",
        "GIER/ASTRONOMY",
        "GIER/CHEMISTRY",
        "GIER/GAMES",
        "GIER/HELP",
        "GIER/HELP3",
        "GIER/MATHEMATICS",
        "GIER/MISC",
        "GIER/TEST",
        "GIER/UTIL",
    )

    ctx.start_examination()

    try:
        os.mkdir("/tmp/_aa")
    except FileExistsError:
        pass

    ctx.produce_html(
       html_dir="/tmp/_aa_gier",
       hexdump_limit=1<<10,
       # link_prefix="http://phk.freebsd.dk/misc/gier/",
    )

    print("Now point your browser at", ctx.link_prefix + '/' + ctx.filename_for(ctx))
