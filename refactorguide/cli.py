"""Console script for refactorguide."""
import argparse
import sys

from refactorguide.config import read_bad_smells, read_logic_pacakges, write_example_config
import configparser
import os
import time

from refactorguide.read_idea import parse_idea
from refactorguide.smells import SmellDependencyCrossModule, SmellDependencyCrossPackage, SmellCylicDependency, \
    find_smells

from refactorguide.markdown_write import console_markdown
from refactorguide.uml_write import console_plant_uml


outputs = {
    "md": console_markdown,
    "uml": console_plant_uml
}

parsers = {
    "idea": parse_idea,
}


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s",
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
    parser.add_argument('--config', nargs=1,
                        help="配置文件，提供分层设计和依赖规则", default="config.ini")
    return parser


def main() -> None:
    args = init_argparse().parse_args()

    logic_pacakges = {}
    # layers = {}
    bad_smells = [SmellDependencyCrossModule(),
                  SmellDependencyCrossPackage(),
                  SmellCylicDependency()]

    cp = configparser.ConfigParser(allow_no_value=True)
    cp.optionxform = str

    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            cp.read_string(f.read())
        logic_pacakges = read_logic_pacakges(cp)
        # layers = read_layers(cp)
        _config_bad_smells = read_bad_smells(cp)
        if len(_config_bad_smells) > 0:
            bad_smells = _config_bad_smells
    else:
        write_example_config(cp, args.config)
    module_dict = parsers[args.parser](args.input, logic_pacakges)
    # module_dict = filter_interested_packages(module_dict, logic_pacakges)

    find_smells(module_dict, bad_smells)

    dt = time.strftime("%Y%m%d-%H-%M", time.localtime())
    for o in args.outputs:
        outputs[o](os.path.join("report-"+dt, o), module_dict)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
