from refactorguide.design_parser import load_design_file
import os
import time
import refactorguide.input_idea as input_idea
from refactorguide.smells import SmellCylicDependency, SmellDependencyCrossModule, SmellDependencyCrossPackage, \
    find_smells
import refactorguide.output_md as output_md
import refactorguide.output_uml as output_uml
import refactorguide.desgin as design
import sys
sys.path.append('../')


def main() -> None:
    load_design_file("example/design.ini")
    print(os.getcwd())
    module_dict = input_idea.read_file(
        "example/index.xml", design.LOGIC_PACKAGES)

    if not design.SMELLS:
        design.set_smells([SmellDependencyCrossModule(),
                           SmellDependencyCrossPackage(),
                           SmellCylicDependency()])

    find_smells(module_dict, design.SMELLS)

    dt = time.strftime("report-%Y%m%d-%H-%M", time.localtime())
    output_md.write_files(os.path.join(dt, 'md'), module_dict)
    output_uml.write_files(os.path.join(dt, 'uml'), module_dict)


if __name__ == "__main__":
    main()
