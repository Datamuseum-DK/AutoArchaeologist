import argparse
import importlib
import os
import sys

from autoarchaeologist import Excavation


class MissingArgumentsError(argparse.ArgumentError):
    def __init__(self, detail):
        super().__init__(None, detail)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.args[0]}"


class NoSuchExcavationError(RuntimeError):
    def __init__(self, excavation_name):
        super().__init__(excavation_name)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.args[0]}"


def action_for_args(args):
    if getattr(args, 'excavator', None):
        return ("excavator", load_excavator_by_name(args.excavator))

    raise MissingArgumentsError("no valid action was requsted")


def load_excavator_by_name(excavator):
    # first try to grab an arbitrary excavation within a single file

    try:
        # directly load the excavator as a named module
        exacations_package = importlib.import_module(excavator)
        return getattr(exacations_package, 'excavation')
    except AttributeError:
        # no excavation property found in the loaded module so error out
        raise NoSuchExcavationError(excavator)
    except ModuleNotFoundError:
        # no such module so proceed to try as a named property within a module
        pass

    # now try to access a named property within a module
    excavaor_parts = excavator.split('.')
    excavation_name = excavaor_parts.pop()
    package_name = '.'.join(excavaor_parts)
    try:
        exacations_package = importlib.import_module(package_name)
        return getattr(exacations_package, excavation_name)
    except Exception as e:
        raise NoSuchExcavationError(excavator)


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default="/tmp/_autoarchaologist")
    parser.add_argument('--excavator',
        help="The name of a file to import that contains an excavation"
             "which will be used to extract information from the artifact.")
    parser.add_argument('filename')

    return parser.parse_args(args=argv)


def process_arguments(args):
    if args.dir == ".":
        args.dir = os.path.join(os.getcwd(), "output", "_autoarchaologist")

    if args.filename:
        args.filename = os.path.abspath(args.filename)

    return args


def perform_excavation(args):
    match action_for_args(args):
        case "excavator", AnExcavation:
            assert issubclass(AnExcavation, Excavation)
            ctx = AnExcavation(html_dir=args.dir)
        case action, _:
            raise NotImplementedError(f"action: {action}")

    ctx.add_file_artifact(args.filename)

    ctx.start_examination()

    return ctx


def main_throwing():
    args = process_arguments(parse_arguments())

    try:
        os.mkdir(args.dir)
    except FileExistsError:
        pass

    ctx = perform_excavation(args)
    ctx.produce_html()
    print("Now point your browser at", ctx.filename_for(ctx).link)


if __name__ == "__main__":
    try:
        main_throwing()
    except Exception as e:
        print(str(e))
        sys.exit(1)
