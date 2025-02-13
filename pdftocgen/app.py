"""The executable of pdftocgen"""

import toml
import sys
import argparse
import pdftocgen
import io

from typing import TextIO
from fitzutils import open_pdf, dump_toc, pprint_toc, get_file_encoding
from .tocgen import gen_toc

def create_parser():
    parser = argparse.ArgumentParser(prog='pdftocgen', description='Generate PDF table of contents from a recipe file.')
    parser.add_argument('pdf_path', metavar='doc.pdf', help='path to the input PDF document')
    parser.add_argument('-r', '--recipe', metavar='recipe.toml', help='path to the recipe file. if this flag is not specified, the default is stdin')
    parser.add_argument('-H', '--human-readable', action='store_true', help='print the toc in a readable format')
    parser.add_argument('-v', '--vpos', action='store_true', help='if this flag is set, the vertical position of each heading will be generated in the output')
    parser.add_argument('-o', '--out', metavar='file', help='path to the output file. if this flag is not specified, the default is stdout')
    parser.add_argument('-g', '--debug', action='store_true', help='enable debug mode')
    parser.add_argument('-V', '--version', action='store_true', help='show version number')
    parser.add_argument('-h', '--help', action='store_true', help='show help')
    return parser

usage_s = """
usage: pdftocgen [options] doc.pdf < recipe.toml
""".strip()

help_s = """
usage: pdftocgen [options] doc.pdf < recipe.toml

Generate PDF table of contents from a recipe file.
""".strip()


This command automatically generates a table of contents for
doc.pdf based on the font attributes and position of
headings specified in a TOML recipe file. See [1] for an
introduction to recipe files.

To generate the table of contents for a pdf, use input
redirection or pipes to supply a recipe file

    $ pdftocgen in.pdf < recipe.toml

or alternatively use the -r flag

    $ pdftocgen -r recipe.toml in.pdf

The output of this command can be directly piped into
pdftocio to generate a new pdf file using the generated
table of contents

    $ pdftocgen -r recipe.toml in.pdf | pdftocio -o out.pdf in.pdf

or you could save the output of this command to a file for
further tweaking using output redirection

    $ pdftocgen -r recipe.toml in.pdf > toc

or the -o flag:

    $ pdftocgen -r recipe.toml -o toc in.pdf

If you only need a readable format of the table of contents,
use the -H flag

    $ pdftocgen -r recipe.toml -H in.pdf

This format cannot be parsed by pdftocio, but it is slightly
more readable.

arguments
  doc.pdf                   path to the input PDF document

options
  -h, --help                show help
  -r, --recipe=recipe.toml  path to the recipe file. if this flag is
                            not specified, the default is stdin
  -H, --human-readable      print the toc in a readable format
  -v, --vpos                if this flag is set, the vertical position
                            of each heading will be generated in the
                            output
  -o, --out=file            path to the output file. if this flag is
                            not specified, the default is stdout
  -g, --debug               enable debug mode
  -V, --version             show version number

[1]: https://krasjet.com/voice/pdf.tocgen/#step-1-build-a-recipe
""".strip()


def main():
    # parse arguments
    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:],
            "hr:Hvo:gV",
            ["help", "recipe=", "human-readable", "vpos", "out=", "debug", "version"]
        )
    except GetoptError as e:
        print(e, file=sys.stderr)
        print(usage_s, file=sys.stderr)
        sys.exit(2)

    recipe_file: TextIO = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
    readable: bool = False
    vpos: bool = False
    out: TextIO = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    debug: bool = False

    for o, a in opts:
        if o in ("-H", "--human-readable"):
            readable = True
        elif o in ("-v", "--vpos"):
            vpos = True
        elif o in ("-r", "--recipe"):
            if opts.recipe:
              try:
                  recipe_file = open(opts.recipe, "r", encoding=get_file_encoding(opts.recipe))
              except IOError as e:
                  print("error: can't open file for reading", file=sys.stderr)
                  print(e, file=sys.stderr)
                  sys.exit(1)
            else:
                recipe_file = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
    try:
        opts, args = parser.parse_args(sys.argv[1:])
    except SystemExit as e:
        print(e, file=sys.stderr)
        print(usage_s, file=sys.stderr)
        sys.exit(2)

    recipe_file: TextIO = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
    readable: bool = False
    vpos: bool = False
    out: Optional[str] = None
    debug: bool = False

    for o in opts:
        if o.long == "--human-readable":
            readable = True
        elif o.long == "--vpos":
            vpos = True
        elif o.long == "--recipe":
            try:
                if opts.recipe:
                    recipe_file = open(opts.recipe, "r", encoding=get_file_encoding(opts.recipe))
                else:
                    recipe_file = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
            except IOError as e:
                print(f"error: can't open recipe file for reading: {e}", file=sys.stderr)
                print(e, file=sys.stderr)
                sys.exit(1)
        elif o.long == "--out":
             if opts.out is None:
                 out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
             else:
                try:
                    out = open(opts.out, "w", encoding='utf-8', errors='ignore')
                except IOError as e:
                    print(f"error: can't open out file for writing: {e}", file=sys.stderr)
                    print(e, file=sys.stderr)
                    sys.exit(1)
        elif o.long == "--debug":
            debug = True
        elif o.long == "--version":
            print("pdfgen", pdftocgen.__version__, file=sys.stderr)
            sys.exit()
        elif o.long == "--help":
            print(help_s, file=sys.stderr)
            sys.exit()

    if len(args) < 1:
        print("error: no input pdf is given", file=sys.stderr)
        print(usage_s, file=sys.stderr)
        sys.exit(1)

    path_in: str = args[0]
    # done parsing arguments
    
    try:
        with open_pdf(path_in) as doc:
            if recipe_file.name == "<stdin>":
                try:
                    recipe = toml.load(open("recipes/default.toml", "r", encoding=get_file_encoding("recipes/default.toml")))
                except IOError as e:
                    print("error: unable to open default recipe", file=sys.stderr)
                    print(e, file=sys.stderr)
                    sys.exit(1)
            else:
              recipe = toml.load(recipe_file)
            toc = gen_toc(doc, recipe)
            if readable:
                print(pprint_toc(toc), file=out)
            else:
                print(dump_toc(toc, vpos), end="", file=out)
    except ValueError as e:
        if debug:
            raise e
        print(f"error: invalid recipe: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        if debug:
            raise e
        print(f"error: unable to open file: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt as e:
        if debug:
            raise e
        print(f"error: interrupted: {e}", file=sys.stderr)
        sys.exit(1)
