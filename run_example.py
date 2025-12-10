
import autoarchaeologist

from autoarchaeologist.generic.bigdigits import BigDigits
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum


if __name__ == "__main__":

    ctx = autoarchaeologist.Excavation()

    ctx.add_examiner(BigDigits)
    ctx.add_examiner(AbsBin)
    ctx.add_examiner(DGC_PaperTapeCheckSum)
    ctx.add_examiner(SameSame)

    ff = ctx.add_file_artifact("examples/30001393.bin")

    ctx.start_examination()

    ctx.produce_html()

    print("Now point your browser at", ctx.filename_for(ctx).link)
