"""Console script for refactorguide."""
import argparse
import sys

from refactorguide.settings_parser import load_settings_file
import os
import time

import refactorguide.input_idea as input_idea
from refactorguide.smells import SmellDependencyCrossModule, SmellDependencyCrossPackage, SmellCylicDependency, \
    find_smells

import refactorguide.output_md as output_md
import refactorguide.output_uml as output_uml

import refactorguide.settings as settings


outputs = {
    "md": output_md.write_files,
    "uml": output_uml.write_files
}

parsers = {
    "idea": input_idea.read_file,
}


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] input",
        description="重构助手，根据你的设计找出代码的坏味道"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version="1.0.0"
    )
    parser.add_argument(
        "-o", "--outputs",
        nargs="*",
        default=["md"],
        choices=outputs.keys(),
        help="报告输出格式，可以同时输出多种格式，默认输出markdown"
    )
    parser.add_argument(
        "-p", "--parser",
        nargs=1,
        default="idea",
        choices=parsers.keys(),
        help="输入文件格式，默认是IDEA的依赖文件格式"
    )
    parser.add_argument('input', help="依赖关系文件")
    parser.add_argument('--settings', nargs=1,
                        help="配置文件，提供分层设计和依赖规则", default="settings.ini")
    return parser


def main() -> None:
    args = init_argparse().parse_args()
    load_settings_file(args.settings, generate_example=True)

    module_dict = parsers[args.parser](args.input, settings.LOGIC_PACKAGES)

    if len(settings.SMELLS) == 0:
        settings.set_smells([SmellDependencyCrossModule(),
                             SmellDependencyCrossPackage(),
                             SmellCylicDependency()])
    find_smells(module_dict, settings.SMELLS)

    dt = time.strftime("%Y%m%d-%H-%M", time.localtime())
    for o in args.outputs:
        outputs[o](os.path.join("report-"+dt, o), module_dict)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
