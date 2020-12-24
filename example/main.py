import refactorguide.settings as settings
import refactorguide.output_uml as output_uml
import refactorguide.output_md as output_md
from refactorguide.smells import find_smells
import refactorguide.input_idea as input_idea
import time
import os
from refactorguide.settings_parser import load_settings_file


def main() -> None:
    load_settings_file("settings.ini")

    module_dict = input_idea.read_file(
        "deps.xml", settings.LOGIC_PACKAGES)

    # settings.set_smells([SmellDependencyCrossModule(),
    #                      SmellDependencyCrossPackage(),
    #                      SmellCylicDependency()])

    find_smells(module_dict, settings.SMELLS)

    dt = time.strftime("report-%Y%m%d-%H-%M", time.localtime())
    output_md.write_files(os.path.join(dt, 'md'), module_dict)
    output_uml.write_files(os.path.join(dt, 'uml'), module_dict)


if __name__ == "__main__":
    main()
