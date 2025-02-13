import sys
import getopt
import pdftocgen
import argparse
import io
import pdftocio
import os.path
import toml

from typing import Optional, TextIO
from fitzutils import open_pdf, dump_toc, pprint_toc, get_file_encoding
from pdftocgen.tocgen import gen_toc
from pdftocio.tocparser import parse_toc
from pdftocio.tocio import write_toc, read_toc
import io
import os
import toml
from pdfxmeta.app import main as pdfxmeta_main

usage_s = """
usage: pdfgen [options] doc.pdf
""".strip()

help_s = """
usage: pdfgen [options] doc.pdf

Generate PDF table of contents from a recipe file.

This command automatically generates a table of contents for
doc.pdf based on the font attributes and position of
headings specified in a TOML recipe file, and then adds that table of contents to the pdf.

To generate the table of contents for a pdf, use input
redirection or pipes to supply a recipe file

    $ pdfgen in.pdf < recipe.toml

or alternatively use the -r flag

    $ pdfgen -r recipe.toml in.pdf

The output of this command is a new pdf file with the table of contents added.

If you only need a readable format of the table of contents,
use the -H flag

    $ pdfgen -r recipe.toml -H in.pdf

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
                            not specified, the default is {input}_out.pdf
  -g, --debug               enable debug mode
  -V, --version             show version number
""".strip()

def create_parser():
    parser = argparse.ArgumentParser(prog='pdfgen', description='Generate PDF table of contents from a recipe file.')
    parser.add_argument('pdf_path', metavar='doc.pdf', help='path to the input PDF document')
    parser.add_argument('-r', '--recipe', metavar='recipe.toml', help='path to the recipe file. if this flag is not specified, the default is a generated recipe')
    parser.add_argument('-H', '--human-readable', action='store_true', help='print the toc in a readable format')
    parser.add_argument('-v', '--vpos', action='store_true', help='if this flag is set, the vertical position of each heading will be generated in the output')
    parser.add_argument('-o', '--out', metavar='file', help='path to the output file. if this flag is not specified, the default is stdout')
    parser.add_argument('-g', '--debug', action='store_true', help='enable debug mode')
    parser.add_argument('-V', '--version', action='store_true', help='show version number')
    parser.add_argument('-h', '--help', action='store_true', help='show help')
    return parser

def generate_recipe(doc, keywords=""):
    """
    Generates a recipe for the given document.
    
    Args:
        doc: The PDF document.
        keywords: Keywords to search for in the document.

    Returns:
        A TOML formatted string that contains the recipe.
    """
    # call pdfxmeta to generate the recipe file
    # this is a placeholder for now, will add the actual implementation later
    # recipe = pdfxmeta_main(["-a","1",path_in,keywords])
    # return recipe

    # hardcode the recipe for now, will change later
    recipe = """
[[heading]]
level = 1
greedy = true
font.name = "Times-Bold"
font.size = 19.92530059814453

[[heading]]
level = 2
greedy = true
font.name = "Times-Bold"
font.size = 11.9552001953125
"""
    return toml.loads(recipe)

def generate_toc_from_recipe(doc, recipe_file):
    """
    Generates a table of contents from a given recipe file.

    Args:
        doc: The PDF document.
        recipe_file: The path to the recipe file.

    Returns:
        The generated table of contents.
    """
    with open(recipe_file, "r") as f:
        recipe = toml.loads(recipe_file)
        return gen_toc(doc, recipe)

def add_toc_to_pdf(doc, toc):
    """
    Adds the given table of contents to the PDF document.

    Args:
        doc: The PDF document.
        toc: The table of contents to add.
    """
    # an input is given, so switch to input mode
    # toc_file: TextIO = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
    # toc = parse_toc(toc_file)
    # write_toc(doc, toc)

    write_toc(doc, toc)
    parser.add_argument('-g', '--debug', action='store_true', help='enable debug mode')
    parser.add_argument('-V', '--version', action='store_true', help='show version number')
    parser.add_argument('-h', '--help', action='store_true', help='show help')
    return parser

def main():
    # parse arguments
    parser = create_parser()
    
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
    
    if recipe_file.isatty():
        try:
            recipe_file = open("recipes/default.toml", "r", encoding=get_file_encoding("recipes/default.toml"))
        except IOError as e:
            print("error: can't open default recipe file for reading", file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)

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
                # an input is given, so switch to input mode
                toc_file: TextIO = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
                toc = parse_toc(toc_file)
                write_toc(doc, toc)
                if out is None:
                    # add suffix to input name as output
                    pfx, ext = os.path.splitext(path_in)
                    out = f"{pfx}_out{ext}"
                doc.save(out)
                

    except ValueError as e:
        if debug:
            raise e
        print(f"error: {e}", file=sys.stderr)
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
    except Exception as e:
        if debug:
            raise e
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
