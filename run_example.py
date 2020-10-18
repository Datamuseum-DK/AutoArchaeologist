
import os

import autoarchaeologist

from autoarchaeologist.generic.bigdigits import BigDigits
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.papertapechecksum import PaperTapeCheckSum
from autoarchaeologist.regnecentralen.papertapechecksum import RC_PTR_CheckSum


if __name__ == "__main__":

    ctx = autoarchaeologist.Excavation()

    ctx.add_examiner(BigDigits)
    ctx.add_examiner(AbsBin)
    ctx.add_examiner(PaperTapeCheckSum)
    ctx.add_examiner(RC_PTR_CheckSum)
    ctx.add_examiner(SameSame)

    ff = ctx.add_file_artifact("examples/30001393.bin")

    ctx.start_examination()

    try:
        os.mkdir("/tmp/_autoarchaologist")
    except FileExistsError:
        pass

    ctx.produce_html(html_dir="/tmp/_autoarchaologist")

    print("Now point your browser at", ctx.link_prefix + '/' + ctx.filename_for(ctx))
