# coding=utf-8
"""
"""
import os
from refactorguide.tools import write_file
from refactorguide.formatters import class_header, dependencies_tree, component_header
from refactorguide.models import Component, Hierarchy, group_class_by_module_package

oneline_md_format = "[{full_name}](../{package}/{name}.md)"


def smells_markdown(component: Component):
    '''Concat dependency and usage'''
    md = "\n## 坏味道依赖有{}项:  \n\n".format(len(component.smell_dependencies))
    md += dependencies_tree(group_class_by_module_package(component.smell_dependencies),
                            oneline_format=oneline_md_format)
    md += "\n--------------------\n"
    md += "\n## 坏味道调用有{}处:  \n\n".format(len(component.smell_usages))
    md += dependencies_tree(group_class_by_module_package(component.smell_usages),
                            oneline_format=oneline_md_format)
    return md


def write_files(report_dir, hierarchy: Hierarchy):
    for layer in hierarchy.layers:
        write_file(os.path.join(report_dir, layer.name), "_layer_.md",
                   component_header(layer,
                                    oneline_format=oneline_md_format) + smells_markdown(layer))
        for module in layer.modules:
            write_file(os.path.join(report_dir, layer.name, module.name), "_module_.md",
                       component_header(module,
                                        oneline_format=oneline_md_format) + smells_markdown(module))
            for package in module.packages:
                write_file(os.path.join(report_dir, layer.name, module.name, package.name), "_pacakge_.md",
                           component_header(package, oneline_format=oneline_md_format) + smells_markdown(package))
                for cls in package.classes:
                    # Todo: dulicate name?
                    write_file(os.path.join(report_dir, layer.name, module.name, package.name), cls.name + ".md",
                               class_header(cls) + smells_markdown(cls))
