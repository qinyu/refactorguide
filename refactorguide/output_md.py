import os
from refactorguide.statistics import components_statistics, dependencies_statistics, smells_statistics, \
    components_statistics_headers, smells_statistics_headers, dependencies_statistics_headers, \
    group_classes_by_smell_dependency
from refactorguide.tools import write_file
from refactorguide.formatters import dependencies_tree
from refactorguide.models import Component, Hierarchy, group_class_by_module_package, ComponentList
from tabulate import tabulate

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
    file_path = os.path.join(_dir, "_%s_smells.md" % type(component_list).__name__)
    write_file(file_path,
               "# 各%s坏味道依赖统计：\n\n" % component_list.item_type.__name__,
               tabulate(components_statistics(component_list.items), components_statistics_headers, tablefmt="github"),
               "\n\n")
    write_file(file_path, _smell_dependencies_md(component_list, oneline_format), "\n\n")
    write_file(file_path, _dependencies_md(component_list, oneline_format), "\n\n")


def _write_class_semll(report_dir, cls):
    file_path = os.path.join(report_dir, cls.layer, cls.module, cls.package, cls.name + ".md")
    write_file(file_path, _smell_dependencies_md(cls, _oneline_class_md_format), "\n\n")
    write_file(file_path, _dependencies_md(cls, _oneline_class_md_format), "\n\n")


def _write_component_list_statistics(report_dir, component_list: ComponentList):
    file_path = os.path.join(report_dir, "_%s_statistics.md" % type(component_list).__name__)
    newmethod687(component_list, file_path)


def newmethod687(component_list, file_path):
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
               "# 各%s坏味道统计：\n\n" % component_list.item_type.__name__,
               tabulate(components_statistics(component_list.items), components_statistics_headers, tablefmt="github"),
               "\n\n")


def _write_layer_summary(report_dir, layer):
    _dir = os.path.join(report_dir, layer.name)
    _write_component_list_smell(_dir, layer, _oneline_layer_md_format)
    _write_component_list_statistics(_dir, layer)


def _write_module_summary(report_dir, module):
    _dir = os.path.join(report_dir, module.layer, module.name)
    _write_component_list_smell(_dir, module, _oneline_module_md_format)
    _write_component_list_statistics(_dir, module)


def _write_pacakge_summary(report_dir, package):
    _dir = os.path.join(report_dir, package.layer, package.module, package.name)
    _write_component_list_smell(_dir, package, _oneline_package_md_format)
    _write_component_list_statistics(_dir, package)


def write_files(report_dir, hierarchy: Hierarchy):
    _write_component_list_statistics(report_dir, hierarchy)
    for layer in hierarchy.layers:
        _write_layer_summary(report_dir, layer)
        for module in layer.modules:
            _write_module_summary(report_dir,  module)
            for package in module.packages:
                _write_pacakge_summary(report_dir, package)
                for cls in package.classes:
                    # Todo: dulicate name?
                    _write_class_semll(report_dir, cls)


def write_files_(report_dir, hierarchy: Hierarchy):
    file_path = os.path.join(report_dir, "_Hierarchy_statistics.md")
    for layer in hierarchy.layers:
        newmethod687(layer, file_path)
        for module in layer.modules:
            _write_module_summary(report_dir,  module)
            newmethod687(module, file_path)
            for package in module.packages:
                _write_pacakge_summary(report_dir, package)
                newmethod687(package, file_path)
                for cls in package.classes:
                    # Todo: dulicate name?
                    _write_class_semll(report_dir, cls)
