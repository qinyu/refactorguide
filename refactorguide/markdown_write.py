# coding=utf-8
import os
from typing import Dict
from refactorguide.utils import export_to_file
from refactorguide.formatters import class_description, dependencies_tree_description, package_description
from refactorguide.model import Component, Package

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


def console_markdown(report_dir, module_dict: Dict[str, Dict[str, Package]]):
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            export_to_file(os.path.join(report_dir, m, p), "_pacakge_.md",
                           package_description(pkg,
                                               oneline_format=oneline_md_format) + smells_markdown_depscription(pkg))
            for cls in pkg.classes:
                export_to_file(os.path.join(report_dir, m, p),  cls.full_name +
                               ".md", class_description(cls) + smells_markdown_depscription(cls))
