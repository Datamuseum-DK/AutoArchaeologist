
import argparse
import os
import sys

import autoarchaeologist

from autoarchaeologist.generic.bigtext import BigText
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum

def parse_arguments(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default="/tmp/_autoarchaologist")

    args = parser.parse_args(args=argv)
    if args.dir == ".":
        args.dir = os.path.join(os.getcwd(), "output", "_autoarchaologist")
    return args

if __name__ == "__main__":
    args = parse_arguments()

    try:
        os.mkdir(args.dir)
    except FileExistsError:
        pass

    ctx = autoarchaeologist.Excavation(html_dir=args.dir)

    ctx.add_examiner(BigText)
    ctx.add_examiner(AbsBin)
    ctx.add_examiner(DGC_PaperTapeCheckSum)
    ctx.add_examiner(SameSame)

    ff = ctx.add_file_artifact("examples/30001393.bin")

    ctx.start_examination()

    ctx.produce_html()

    print("Now point your browser at", ctx.filename_for(ctx).link)
