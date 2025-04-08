import argparse
import importlib
import os
import sys

from autoarchaeologist import Excavation

EXCAVATORS = [
    'examples.showcase'
]


def action_for_args(args):
    if args.excavator is not None:
        return ("excavator", load_excavator_by_name(args.excavator))
    else:
        raise argparse.ArgumentError(None, "no valid excavation was requsted")


def load_excavator_by_name(excavator):
    package_name, excavation_prefix = excavator.split('.')
    excavation_name = f"{excavation_prefix}_excavation"

    exacations_package = importlib.import_module(package_name)
    return getattr(exacations_package, excavation_name)


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default="/tmp/_autoarchaologist")
    parser.add_argument('--excavator', choices=EXCAVATORS)
    parser.add_argument('filename')

    return parser.parse_args(args=argv)


def process_arguments(args):
    if args.dir == ".":
        args.dir = os.path.join(os.getcwd(), "output", "_autoarchaologist")
    if args.filename is not None:
        args.filename = os.path.abspath(args.filename)
    else:
        raise ValueError()

    return args


def perform_excavation(args):
    match action_for_args(args):
        case "excavator", AnExcavation:
            assert issubclass(AnExcavation, Excavation)
            ctx = AnExcavation(html_dir=args.dir)
        case action, _:
            raise NotImplementedError(f"action: {action}")

    ff = ctx.add_file_artifact(args.filename)

    ctx.start_examination()

    return ctx


if __name__ == "__main__":
    args = process_arguments(parse_arguments())

    try:
        os.mkdir(args.dir)
    except FileExistsError:
        pass

    ctx = perform_excavation(args)
    ctx.produce_html()
    print("Now point your browser at", ctx.filename_for(ctx).link)
