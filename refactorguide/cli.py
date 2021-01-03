# -*- coding: utf-8 -*-
"""Console script for refactorguide."""
import argparse
from refactorguide.models import Hierarchy
from refactorguide.hierarchy import build_hierarchy, filter_hierarchy
import refactorguide
import sys

from refactorguide.design_parser import load_design_file
import os
import time

import refactorguide.input_idea as input_idea
from refactorguide.smells import find_smells

import refactorguide.output_md as output_md
import refactorguide.output_uml as output_uml

import refactorguide.desgin as design


output_formats = {
    "md": output_md.write_files,
    "uml": output_uml.write_files
}

input_parsers = {
    "idea": input_idea.read_file,
}


def __init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] index design",
        description="Refactor guide, find smells between your code and desired design"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=refactorguide.__version__
    )
    parser.add_argument(
        "-o", "--outputs",
        nargs="*",
        default=["md"],
        choices=output_formats.keys(),
        help="Specify format of report, you can specify more than one format."
    )
    parser.add_argument(
        "-p", "--parser",
        nargs=1,
        default="idea",
        choices=input_parsers.keys(),
        help="Parser used to parse the 'index' file. "
        "Only IDEA dependency index file is supported."
    )

    parser.add_argument(
        "-f", "--filters",
        nargs="*",
        default=[""],
        help=r"Filter the result, use pattern linke \"{layer}:{package}:{module}:{class}\""
    )
    parser.add_argument(
        'index', help="Path of dependencies index file of current code."
        "Use 'Dependency analyse..' action in IDEA to export.")
    parser.add_argument(
        'design', help="Path of the desired design file."
        "A sample will be created if file doesn't exist.")
    return parser


def main() -> None:
    args = __init_argparse().parse_args()
    load_design_file(args.design, generate_example=True)

    full_hierarchy = build_hierarchy(input_parsers[args.parser](args.index),
                                     design.LAYERS, design.LOGIC_PACKAGES)

    hierarchy = Hierarchy()
    for f in args.filters:
        hierarchy = filter_hierarchy(full_hierarchy, f, hierarchy)

    find_smells(hierarchy, design.SMELLS)

    timestamp = time.strftime("%Y%m%d-%H-%M", time.localtime())
    for format_key in args.outputs:
        output_formats[format_key](os.path.join(
            "report-"+timestamp, format_key), hierarchy)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
