import os
import sys
from types import SimpleNamespace

from autoarchaeologist.__main__ import parse_arguments, process_arguments, perform_excavation
from examples import ShowcaseExcacation

if __name__ == "__main__":
    argv = sys.argv[1:]
    # force the example as the filename
    argv.append("examples/30001393.bin")
    args = process_arguments(parse_arguments(argv=argv))

    ctx = perform_excavation(args, ("excavator", ShowcaseExcacation))
    ctx.produce_html()

    print("Now point your browser at", ctx.filename_for(ctx).link)
