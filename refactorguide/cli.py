"""Console script for refactorguide."""
import argparse
import refactorguide
import sys

from refactorguide.design_parser import load_design_file
import os
import time

import refactorguide.input_idea as input_idea
from refactorguide.smells import SmellDependencyCrossModule, SmellDependencyCrossPackage, SmellCylicDependency, \
    find_smells

import refactorguide.output_md as output_md
import refactorguide.output_uml as output_uml

import refactorguide.desgin as desgin


outputs = {
    "md": output_md.write_files,
    "uml": output_uml.write_files
}

parsers = {
    "idea": input_idea.read_file,
}


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] index design",
        description="重构助手，根据你的设计找出代码的坏味道"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=refactorguide.__version__
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
    parser.add_argument('index', help="依赖关系文件，目前只支持IDEA中导出的依赖关系文件")
    parser.add_argument(
        'design', help="设计文件，提供包设计、层设计和依赖坏味道。如指定文件不存在，会自动生成一个，在此基础上进行设计")
    return parser


def main() -> None:
    args = init_argparse().parse_args()
    load_design_file(args.design, generate_example=True)

    module_dict = parsers[args.parser](args.index, desgin.LOGIC_PACKAGES)

    if len(desgin.SMELLS) == 0:
        desgin.set_smells([SmellDependencyCrossModule(),
                           SmellDependencyCrossPackage(),
                           SmellCylicDependency()])
    find_smells(module_dict, desgin.SMELLS)

    dt = time.strftime("%Y%m%d-%H-%M", time.localtime())
    for o in args.outputs:
        outputs[o](os.path.join("report-"+dt, o), module_dict)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
