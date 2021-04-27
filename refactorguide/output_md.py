# coding=utf-8
import os
from refactorguide.statistics import components_statistics, dependencies_statistics, smells_statistics, \
    components_statistics_headers, smells_statistics_headers, dependencies_statistics_headers, \
    group_classes_by_smell_dependency
from refactorguide.tools import write_file
from refactorguide.formatters import dependencies_tree
from refactorguide.models import Component, Hierarchy, group_class_by_module_package
from tabulate import tabulate

_oneline_layer_md_format = "[{full_name}](../{layer}/{module}/{package}/{name}.md)"
_oneline_module_md_format = "[{full_name}](../../{layer}/{module}/{package}/{name}.md)"
_oneline_package_md_format = "[{full_name}](../../../{layer}/{module}/{package}/{name}.md)"
_oneline_class_md_format = "[{full_name}](../../../{layer}/{module}/{package}/{name}.md)"
_md_line = "\n--------------------\n"

headers = ["Name", "Dep. Count", "Smell Dep. Count", "Class Count", "Smell Class Count"]


def _smell_dependencies_md(component, oneline_format):
    md = ""
    dependency_smell_count = len(component.smell_dependencies)
    if dependency_smell_count > 0:
        md = _md_line
        md += "\n## 坏味道依赖有{}项:  \n\n".format(dependency_smell_count)
        md += dependencies_tree(group_class_by_module_package(component.smell_dependencies),
                                oneline_format)
    return md


def _dependencies_md(component: Component, oneline_format):
    md = ""
    dependency_count = len(component.dependencies)
    if dependency_count > 0:
        md += _md_line
        md += "\n## 全部依赖共有{}项:  \n\n".format(dependency_count)
        md += dependencies_tree(group_class_by_module_package(component.dependencies), oneline_format)
    return md


def _usages_md(component: Component, oneline_format):
    md = ""
    usage_count = len(component.usages)
    if usage_count > 0:
        md += _md_line
        md += "\n## 全部调用共有{}项:  \n\n".format(usage_count)
        md += dependencies_tree(group_class_by_module_package(component.usages), oneline_format)
    return md


def _smell_usages_md(component: Component, oneline_format):
    md = ""
    usage_smell_count = len(component.smell_usages)
    if usage_smell_count > 0:
        md += _md_line
        md += "\n## 坏味道调用有{}处:  \n\n".format(usage_smell_count)
        md += dependencies_tree(group_class_by_module_package(component.smell_usages),
                                oneline_format)
    return md


def _write_class_summary(report_dir, cls):
    _dir = os.path.join(report_dir, cls.layer, cls.module, cls.package)
    write_file(_dir,
               cls.name + ".md",
               #    class_header(cls),
               _smell_dependencies_md(cls, _oneline_class_md_format),
               _dependencies_md(cls, _oneline_class_md_format))


def _write_pacakge_summary(report_dir, package):
    _dir = os.path.join(report_dir, package.layer, package.module, package.name)
    write_file(_dir,
               package.name + "_pacakge.md",
               "各class坏味道依赖统计：\n",
               tabulate(components_statistics(
                   package.items), components_statistics_headers, tablefmt="github"),
               _smell_dependencies_md(package, _oneline_package_md_format),
               _dependencies_md(package, _oneline_package_md_format))


def _write_module_summary(report_dir, module):
    _dir = os.path.join(report_dir, module.layer, module.name)
    write_file(_dir,
               module.name + "_module.md",
               "各package坏味道依赖统计：\n",
               tabulate(components_statistics(module.items), components_statistics_headers, tablefmt="github"),
               _smell_dependencies_md(module, _oneline_module_md_format),
               _dependencies_md(module, _oneline_module_md_format))


def _write_layer_summary(report_dir, layer):
    write_file(os.path.join(report_dir, layer.name),
               layer.name + "_layer.md",
               "各module坏味道依赖统计：\n",
               tabulate(components_statistics(layer.items), components_statistics_headers, tablefmt="github"),
               _smell_dependencies_md(layer, _oneline_layer_md_format),
               _dependencies_md(layer, _oneline_layer_md_format))


def _write_hierarchy_summary(report_dir, hierarchy):
    s_d_c = group_classes_by_smell_dependency(hierarchy.classes)

    write_file(os.path.join(report_dir), "summary.md",
               "各smell影响范围统计：\n",
               tabulate(smells_statistics(s_d_c), smells_statistics_headers, tablefmt="github"),
               _md_line,
               "\n\n".join([tabulate(dependencies_statistics(d_c), dependencies_statistics_headers, tablefmt="github")
                            for s, d_c in s_d_c.items()]),
               _md_line,
               tabulate(components_statistics(hierarchy.items), components_statistics_headers, tablefmt="github"))


def write_files(report_dir, hierarchy: Hierarchy):
    _write_hierarchy_summary(report_dir, hierarchy)
    for layer in hierarchy.layers:
        _write_layer_summary(report_dir, layer)
        for module in layer.modules:
            _write_module_summary(report_dir,  module)
            for package in module.packages:
                _write_pacakge_summary(report_dir, package)
                for cls in package.classes:
                    # Todo: dulicate name?
                    _write_class_summary(report_dir, cls)
