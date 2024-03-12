import os
from run import process_arguments, perform_excavation
from types import SimpleNamespace

from autoarchaeologist.base.excavation import Excavation
from autoarchaeologist.generic.bigdigits import BigDigits
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")

class ExampleExcavation(Excavation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(BigDigits)
        self.add_examiner(AbsBin)
        self.add_examiner(DGC_PaperTapeCheckSum)
        self.add_examiner(SameSame)

def process_example(*, html_dir):
    example_arguments = SimpleNamespace()
    example_arguments.dir = html_dir
    example_arguments.filename = os.path.join(EXAMPLES_DIR, "30001393.bin")
    args = process_arguments(example_arguments)

    try:
        os.mkdir(args.dir)
    except FileExistsError:
        pass

    return perform_excavation(args, ("excavator", ExampleExcavation))

if __name__ == "__main__":
    ctx = process_example(html_dir=".")
    ctx.produce_html()
    print("Now point your browser at", ctx.filename_for(ctx).link)
