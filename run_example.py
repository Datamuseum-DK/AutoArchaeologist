import os
import sys
from types import SimpleNamespace

from run import parse_arguments, process_arguments, perform_excavation
from autoarchaeologist.base.excavation import Excavation
from autoarchaeologist.generic.bigtext import BigText
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum


class ExampleExcavation(Excavation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(BigText)
        self.add_examiner(AbsBin)
        self.add_examiner(DGC_PaperTapeCheckSum)
        self.add_examiner(SameSame)


if __name__ == "__main__":
    argv = sys.argv[1:]
    # force the example as the filename
    argv.append("examples/30001393.bin")
    args = process_arguments(parse_arguments(argv=argv))

    ctx = perform_excavation(args, ("excavator", ExampleExcavation))
    ctx.produce_html()

    print("Now point your browser at", ctx.filename_for(ctx).link)
