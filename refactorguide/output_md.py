# coding=utf-8
import os
from typing import Dict
from refactorguide.tools import write_file
from refactorguide.formatters import class_description, dependencies_tree_description, package_description
from refactorguide.models import Component, Package

oneline_md_format = "[{full_name}](../{package}/{full_name}.md)"


def smells_markdown_depscription(component: Component):
    md = "\n## 坏味道依赖有{}项:  \n\n".format(len(component.smell_dependencies))
    md += dependencies_tree_description(component.grouped_smell_dependencies,
                                        oneline_format=oneline_md_format)
    md += "\n--------------------\n"
    md += "\n## 坏味道调用有{}处:  \n\n".format(len(component.smell_usages))
    md += dependencies_tree_description(component.grouped_smell_usages,
                                        oneline_format=oneline_md_format)
    return md


def write_files(report_dir, module_dict: Dict[str, Dict[str, Package]]):
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            write_file(os.path.join(report_dir, m, p), "_pacakge_.md",
                       package_description(pkg,
                                           oneline_format=oneline_md_format) + smells_markdown_depscription(pkg))
            for cls in pkg.classes:
                write_file(os.path.join(report_dir, m, p),  cls.logic_name +
                           ".md", class_description(cls) + smells_markdown_depscription(cls))
