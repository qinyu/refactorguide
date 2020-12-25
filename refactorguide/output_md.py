# coding=utf-8
"""
"""
import os
from typing import Dict
from refactorguide.tools import write_file
from refactorguide.formatters import class_header, dependencies_tree, component_header
from refactorguide.models import Component, Module

oneline_md_format = "[{full_name}](../{package}/{logic_name}.md)"


def smells_markdown(component: Component):
    '''Concat dependency and usage'''
    md = "\n## 坏味道依赖有{}项:  \n\n".format(len(component.smell_dependencies))
    md += dependencies_tree(component.grouped_smell_dependencies,
                            oneline_format=oneline_md_format)
    md += "\n--------------------\n"
    md += "\n## 坏味道调用有{}处:  \n\n".format(len(component.smell_usages))
    md += dependencies_tree(component.grouped_smell_usages,
                            oneline_format=oneline_md_format)
    return md


def write_files(report_dir, module_dict: Dict[str, Module]):
    for m, module in module_dict.items():
        write_file(os.path.join(report_dir, m), "_module_.md",
                   component_header(module,
                                    oneline_format=oneline_md_format) + smells_markdown(module))
        for pkg in module.packages:
            write_file(os.path.join(report_dir, m, pkg.name), "_pacakge_.md",
                       component_header(pkg, oneline_format=oneline_md_format) + smells_markdown(pkg))
            for cls in pkg.classes:
                write_file(os.path.join(report_dir, m, pkg.name),  cls.logic_name + ".md",
                           class_header(cls) + smells_markdown(cls))
