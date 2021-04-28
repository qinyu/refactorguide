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
_md_line = "\n\n" + "-" * 80 + "\n\n"


def _smell_dependencies_md(component: Component, oneline_format):
    md = ""
    dependency_smell_count = len(component.smell_dependencies)
    if dependency_smell_count > 0:
        md = _md_line
        md += "\n## 坏味道依赖有{}项:  \n\n".format(dependency_smell_count)
        md += dependencies_tree(group_class_by_module_package(set(component.smell_dependencies)),
                                oneline_format)
    return md


def _dependencies_md(component: Component, oneline_format):
    md = ""
    dependency_count = len(component.dependencies)
    if dependency_count > 0:
        md += _md_line
        md += "\n## 全部依赖共有{}项:  \n\n".format(dependency_count)
        md += dependencies_tree(group_class_by_module_package(set(component.dependencies)), oneline_format)
    return md


def _usages_md(component: Component, oneline_format):
    md = ""
    usage_count = len(component.usages)
    if usage_count > 0:
        md += _md_line
        md += "\n## 全部调用共有{}项:  \n\n".format(usage_count)
        md += dependencies_tree(group_class_by_module_package(set(component.usages)), oneline_format)
    return md


def _smell_usages_md(component: Component, oneline_format):
    md = ""
    usage_smell_count = len(component.smell_usages)
    if usage_smell_count > 0:
        md += _md_line
        md += "\n## 坏味道调用有{}处:  \n\n".format(usage_smell_count)
        md += dependencies_tree(group_class_by_module_package(set(component.smell_usages)),
                                oneline_format)
    return md


def _write_component_list_smell(_dir, component_list: ComponentList, oneline_format):
    write_file(_dir,
               "_%s_smells.md" % type(component_list).__name__,
               "各%s坏味道依赖统计：\n" % component_list.item_type.__name__,
               tabulate(components_statistics(component_list.items), components_statistics_headers, tablefmt="github"),
               _smell_dependencies_md(component_list, oneline_format),
               _dependencies_md(component_list, oneline_format))


def _write_class_semll(report_dir, cls):
    _dir = os.path.join(report_dir, cls.layer, cls.module, cls.package)
    write_file(_dir,
               cls.name + ".md",
               _smell_dependencies_md(cls, _oneline_class_md_format),
               _dependencies_md(cls, _oneline_class_md_format))


def _write_component_list_statistics(report_dir, component_list: ComponentList):
    sdc_dict = group_classes_by_smell_dependency(component_list.classes)

    smells_list = ["## " + str(s) + "影响范围统计：\n\n" +
                   tabulate(dependencies_statistics(dc),
                            dependencies_statistics_headers,
                            tablefmt="github") for s, dc in sdc_dict.items()]
    write_file(os.path.join(report_dir),
               "_%s_statistics.md" % type(component_list).__name__,
               "# 各Smell影响范围统计：\n\n",
               tabulate(smells_statistics(sdc_dict), smells_statistics_headers, tablefmt="github"),
               _md_line,
               "\n\n".join(smells_list),
               _md_line,
               "# 各%s坏味道统计：\n\n" % component_list.item_type.__name__,
               tabulate(components_statistics(component_list.items), components_statistics_headers, tablefmt="github"))


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
