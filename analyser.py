import xml.etree.ElementTree as ET
from config import *

from model import CLS, DEP, PKG, print_class_with_dependencies, print_package_with_dependencies, grouped_by_modules_and_logic_packages
from uml_write import console_plant_uml
from statistics import console_statistics_data
from markdown_write import console_markdown
from functools import reduce


def parse_class(file_node):
    path = file_node.get("path")
    match = category_re_dict["Production"].match(path)
    if match:
        dependencies = [parse_dependency(d)
                        for d in file_node.findall("dependency")]
        return CLS(dependencies=sorted([d for d in dependencies if d], key=sorter), **match.groupdict())
    print("Warning: class missed %s" % path)
    return None


def parse_dependency(dependency_node):
    dep = None
    path = dependency_node.get("path")

    for cat, compiled_re in category_re_dict.items():
        match = compiled_re.match(path)
        if match:
            dep = DEP(category=cat, **match.groupdict())
            break

    if not dep:
        print("Warning: dependency missed %s" % path)
    return dep


def parse_dependencies(file_node):
    dependencies = [parse_dependency(d)
                    for d in file_node.findall("dependency")]
    return [d for d in dependencies if d]


def parse_classes_with_dependencies(file_name, class_path_filter=lambda path: True):
    tree = ET.parse(file_name)
    root = tree.getroot()
    return [parse_class(f) for f in root.findall("file") if class_path_filter(f.get("path"))]


def update_class_logic_packages(m_cls_list):
    def update(c):
        for logic_package in logic_pacakges.get(c.module, []):
            if c.logic_package.startswith(logic_package):
                c.logic_package = logic_package
                break
        return c

    for c in m_cls_list:
        update(c)
        c.dependencies = [update(d) for d in c.dependencies]
        c.usages = [update(u) for u in c.usages]


def group_by_modules_and_logic_packages(classes):
    module_dict = grouped_by_modules_and_logic_packages(classes)
    for m, package_dict in module_dict.items():
        for p, p_cls_list in package_dict.items():
            package_dict[p] = PKG(m, p, p_cls_list)

    return module_dict


def find_smells(module_dict):
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            for c in pkg.classes:
                for d in c.dependencies:
                    for smell in dependency_smells:
                        if smell(c, d):
                            d.bad_smells.append(smell)
                for u in c.usages:
                    for smell in usage_smells:
                        if smell(u, c):
                            u.bad_smells.append(smell)


def update_class_usages(class_list):
    class_map = dict((c.path, c) for c in all_classes)

    for u in class_list:
        for d in u.dependencies:
            c = class_map.get(d.path)
            if c:
                for cat, compiled_re in category_re_dict.items():
                    if compiled_re.match(c.path):
                        c.usages.append(DEP(u.path, u.name, u.package,
                                            u.module, cat, u.logic_package))
                        break

    for c in class_list:
        c.usages = sorted(c.usages, key=sorter)


def filter_interested_packages(module_dict, module_packages):
    _m_dict = {}
    for m in module_packages.keys():
        _p_dict = {}
        if m in module_dict.keys():
            for p in module_packages[m]:
                if p in module_dict[m].keys():
                    _p_dict[p] = module_dict[m][p]
                else:
                    print("Warning: interested pacakge missed %s:%s" % (m, p))
            _m_dict[m] = _p_dict
        else:
            print("Warning: interested module missed %s" % m)
    return _m_dict


def filter_interested_modules(module_dict, module_packages):
    _m_dict = {}
    for m in module_packages.keys():
        if m in module_dict.keys():
            _m_dict[m] = module_dict[m]
        else:
            print("Warning: interested module missed %s" % m)
    return _m_dict


pd_format = """
包：{}
================================================================================
一共有依赖 {} 项，坏味道依赖 {} 项
一共有调用 {} 处，坏味道调用 {} 处
--------------------------------------------------------------------------------
包中依赖最多前3个类坏味道依赖共计{}项（占比{}），它们是：
{}
--------------------------------------------------------------------------------
包中调用最多前3个类坏味道调用共计{}处（占比{}），它们是：
{}
--------------------------------------------------------------------------------
"""


def package_description(pkg: PKG):

    def _percenet(sub, total):
        return '{:.2%}'.format(sub/total if total > 0 else 0)

    smell_dependencies_count = len(pkg.suspicious_dependencies)
    smell_usages_count = len(pkg.suspicious_usages)
    top_smell_dependencies_classes = sorted(
        pkg.classes, key=lambda c: len(c.suspicious_dependencies), reverse=True)[:3]
    top_smell_dependencies_count = len(
        set([d for c in top_smell_dependencies_classes for d in c.suspicious_dependencies])) if smell_dependencies_count > 0 else 0
    top_smell_usages_classes = sorted(
        pkg.classes, key=lambda c: len(c.suspicious_usages), reverse=True)[:3]
    top_smell_usages_count = len(
        set([d for c in top_smell_usages_classes for d in c.suspicious_usages])) if smell_usages_count > 0 else 0
    return pd_format.format(
        pkg.name,
        len(pkg.dependencies),
        smell_dependencies_count,
        len(pkg.usages),
        smell_usages_count,
        top_smell_dependencies_count,
        '{:.2%}'.format(
            top_smell_dependencies_count/smell_dependencies_count if smell_dependencies_count > 0 else 0),
        "\n".join(
            ["{}（{}）".format(c.full_name, _percenet(len(set(c.suspicious_dependencies)), smell_dependencies_count)) for c in top_smell_dependencies_classes]),
        top_smell_usages_count,
        '{:.2%}'.format(
            top_smell_usages_count/smell_usages_count if smell_usages_count > 0 else 0),
        "\n".join(
            ["{}（{}）".format(c.full_name, _percenet(len(set(c.suspicious_usages)), smell_usages_count)) for c in top_smell_usages_classes]),
    )


if __name__ == "__main__":
    all_classes = [c for c in parse_classes_with_dependencies(
        "fast_hub_deps.xml", class_path_filter) if c]
    update_class_logic_packages(all_classes)
    update_class_usages(all_classes)

    module_dict = group_by_modules_and_logic_packages(all_classes)
    # module_dict = filter_interested_packages(module_dict, logic_pacakges)

    find_smells(module_dict)
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            # print_package_with_dependencies(pkg, True)
            print(package_description(pkg))
            # for c in pkg.classes:
            # print_class_with_dependencies(c, True)
            # break
        break

    # console_markdown(module_dict)
    # console_plant_uml(module_dict)
