# run this file from example dir, not from repo root
import time
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from refactorguide.hierarchy import build_hierarchy, filter_hierarchy  # noqa: E402,E261
from refactorguide.design_parser import load_design  # noqa: E402,E261
import refactorguide.input_idea as input_idea  # noqa: E402,E261
from refactorguide.smells import find_smells  # noqa: E402,E261
import refactorguide.output_md as output_md  # noqa: E402,E261
import refactorguide.output_uml as output_uml  # noqa: E402,E261
from refactorguide.models import Hierarchy  # noqa: E402,E261


def main() -> None:
    design = load_design("design.ini")

    full_hierarchy = build_hierarchy(input_idea.read_file("index.xml"),
                                     design.layers)
    hierarchy = filter_hierarchy(
        full_hierarchy, "unknown:app:com.fastaccess:A*", Hierarchy())

    find_smells(hierarchy, design.smells)

    dt = time.strftime("report-%Y%m%d-%H-%M", time.localtime())
    output_md.write_files(os.path.join(dt, 'md'), hierarchy)
    output_uml.write_files(os.path.join(dt, 'uml'), hierarchy)


if __name__ == "__main__":
    main()
