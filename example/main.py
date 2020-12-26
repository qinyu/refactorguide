from refactorguide.hierachy import build_hierachy
from refactorguide.design_parser import load_design_file
import os
import time
import refactorguide.input_idea as input_idea
from refactorguide.smells import find_smells
import refactorguide.output_md as output_md
import refactorguide.output_uml as output_uml
import refactorguide.desgin as design
import sys
sys.path.append('../')


def main() -> None:
    load_design_file("example/design.ini")
    print(os.getcwd())

    hierarchy = build_hierachy(input_idea.read_file("example/index.xml"),
                               design.LAYERS, design.LOGIC_PACKAGES)

    find_smells(hierarchy, design.SMELLS)

    dt = time.strftime("report-%Y%m%d-%H-%M", time.localtime())
    output_md.write_files(os.path.join(dt, 'md'), hierarchy)
    output_uml.write_files(os.path.join(dt, 'uml'), hierarchy)


if __name__ == "__main__":
    main()
