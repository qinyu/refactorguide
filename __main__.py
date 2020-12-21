

import os
import argparse
import time

from config import logic_pacakges, dependency_smells, usage_smells

from parsers import parse_idea
from smells import find_smells
from filters import filter_interested_packages

from markdown_write import console_markdown
from uml_write import console_plant_uml


outputs = {
    "md": console_markdown,
    "uml": console_plant_uml
}

parsers = {
    "idea": parse_idea,
}


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [INPUT] [CONFIG]",
        description="代码分析"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 1.0.0"
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
    # parser.add_argument('input', nargs=1, help="依赖关系文件")
    # parser.add_argument('config', nargs=1, help="配置文件")
    return parser


def main() -> None:
    args = init_argparse().parse_args()
    module_dict = parsers[args.parser](
        "fast_hub_deps.xml", logic_pacakges)
    # module_dict = filter_interested_packages(module_dict, logic_pacakges)

    find_smells(module_dict, dependency_smells, usage_smells)

    dt = time.strftime("%Y%m%d-%H-%M", time.localtime())
    for o in args.outputs:
        outputs[o](os.path.join("report-"+dt, o), module_dict)


main()
