from tabulate import tabulate
from refactorguide.models import Component, Hierarchy, group_class_by_module_package, ComponentList
from refactorguide.formatters import dependencies_tree
from refactorguide.tools import write_file
import pandas as pd

import os
from refactorguide.statistics import components_statistics, dependencies_statistics,\
    smell_data_frame, smells_statistics,\
    components_statistics_headers, smells_statistics_headers, dependencies_statistics_headers,\
    group_classes_by_smell_dependency

_oneline_layer_md_format = "[{full_name}](../{layer}/{module}/{package}/{name}.md)"
_oneline_module_md_format = "[{full_name}](../../{layer}/{module}/{package}/{name}.md)"
_oneline_package_md_format = "[{full_name}](../../../{layer}/{module}/{package}/{name}.md)"
_oneline_class_md_format = "[{full_name}](../../../{layer}/{module}/{package}/{name}.md)"


def _smell_dependencies_md(component: Component, oneline_format):
    md = ""
    dependency_smell_count = len(component.smell_dependencies)
    if dependency_smell_count > 0:
        md += "## 坏味道依赖有{}项:  \n\n".format(dependency_smell_count)
        md += dependencies_tree(group_class_by_module_package(set(component.smell_dependencies)),
                                oneline_format)
    return md


def _dependencies_md(component: Component, oneline_format):
    md = ""
    dependency_count = len(component.dependencies)
    if dependency_count > 0:
        md += "## 全部依赖共有{}项:  \n\n".format(dependency_count)
        md += dependencies_tree(group_class_by_module_package(set(component.dependencies)), oneline_format)
    return md


def _write_component_list_smell(_dir, component_list: ComponentList, oneline_format):
    file_path = os.path.join(_dir, "_%s_smells.md" % str.lower(type(component_list).__name__))
    write_file(file_path, str(component_list.hierarchy_path), "\n\n")
    write_file(file_path,
               "# 各%s坏味道依赖统计：\n\n" % str.lower(component_list.item_type.__name__),
               tabulate(components_statistics(component_list.items), components_statistics_headers, tablefmt="github"),
               "\n\n")
    _write_component_list_statistics_file(component_list, file_path)
    write_file(file_path, _smell_dependencies_md(component_list, oneline_format), "\n\n")
    write_file(file_path, _dependencies_md(component_list, oneline_format), "\n\n")


def _write_class_semll(report_dir, cls):
    file_path = os.path.join(report_dir, cls.layer, cls.module, cls.package, cls.name + ".md")
    write_file(file_path, str(cls.hierarchy_path), "\n\n")

    write_file(file_path, _smell_dependencies_md(cls, _oneline_class_md_format), "\n\n")
    write_file(file_path, _dependencies_md(cls, _oneline_class_md_format), "\n\n")


def _write_component_list_statistics_file(component_list, file_path):
    sdc_dict = group_classes_by_smell_dependency(component_list.classes)

    smells_list = ["## " + str(s) + "影响统计：\n\n" +
                   tabulate(dependencies_statistics(dc),
                            dependencies_statistics_headers,
                            tablefmt="github") for s, dc in sdc_dict.items()]
    write_file(file_path,
               "# 全部Smell影响统计：\n\n",
               tabulate(smells_statistics(sdc_dict), smells_statistics_headers, tablefmt="github"),
               "\n\n")
    write_file(file_path,
               "\n\n".join(smells_list),
               "\n\n",
               "# 各%s坏味道统计：\n\n" % str.lower(component_list.item_type.__name__),
               tabulate(components_statistics(component_list.items), components_statistics_headers, tablefmt="github"),
               "\n\n")


def _write_layer_summary(report_dir, layer):
    _dir = os.path.join(report_dir, layer.name)
    _write_component_list_smell(_dir, layer, _oneline_layer_md_format)


def _write_module_summary(report_dir, module):
    _dir = os.path.join(report_dir, module.layer, module.name)
    _write_component_list_smell(_dir, module, _oneline_module_md_format)


def _write_pacakge_summary(report_dir, package):
    _dir = os.path.join(report_dir, package.layer, package.module, package.name)
    _write_component_list_smell(_dir, package, _oneline_package_md_format)


def write_files(report_dir, hierarchy: Hierarchy):
    data = smell_data_frame(hierarchy.classes)

    layer_count = data.groupby(["Smell.Str",
                                "Dep.Path",
                                "Cls.Layer"]).agg(Count=("Cls.Path", "count"))

    module_count = data.groupby(["Smell.Str",
                                 "Dep.Path",
                                 "Cls.Layer",
                                 "Cls.Module"]).agg(Count=("Cls.Path", "count"))
    package_count = data.groupby(["Smell.Str",
                                  "Dep.Path",
                                  "Cls.Layer",
                                  "Cls.Module",
                                  "Cls.Package"]).agg(Count=("Cls.Path", "count"))
    smell_group = data.groupby(["Smell.Str",
                                "Dep.Path",
                                "Cls.Layer",
                                "Cls.Module",
                                "Cls.Package",
                                "Cls.Name",
                                "Cls.Path"]
                               ).agg(Count=("Cls.Path", "count"))

    file_path = os.path.join(report_dir, 'smell_statistics.xlsx')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with pd.ExcelWriter(file_path) as writer:
        layer_count.to_excel(writer, sheet_name="Smells Count per Layer")
        module_count.to_excel(writer, sheet_name="Smells Count per module")
        package_count.to_excel(writer, sheet_name="Smells Count per Package")
        smell_group.to_excel(writer, sheet_name="Smells List")

    for layer in hierarchy.layers:
        _write_layer_summary(report_dir, layer)
        for module in layer.modules:
            _write_module_summary(report_dir,  module)
            for package in module.packages:
                _write_pacakge_summary(report_dir, package)
                for cls in package.classes:
                    # Todo: dulicate name?
                    _write_class_semll(report_dir, cls)
