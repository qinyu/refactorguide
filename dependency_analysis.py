import xml.etree.ElementTree as ET
import re
from functools import partial
from itertools import groupby
from operator import attrgetter
from config import category_re_dict, class_path_filter, dependency_filter, logic_pacakges

from model import CLS, DEP, PKG, print_class_with_dependencies, print_package_with_dependencies
from uml import console_plant_uml
from statistics import console_statistics_data
from markdown import console_markdown


def parse_class(file_node):
    path = file_node.get("path")
    match = category_re_dict["Production"].match(path)
    if match:
        dependencies = [parse_dependency(d)
                        for d in file_node.findall("dependency")]
        return CLS(dependencies=sorted([d for d in dependencies if d], key=attrgetter('module', 'logic_package', 'package', 'name')), **match.groupdict())
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


def update_logic_package(c):
    for logic_package in logic_pacakges.get(c.module, []):
        if c.logic_package.startswith(logic_package):
            c.logic_package = logic_package
            break
    return c


def group_by_modules_and_logic_packages(file_list):
    module_dict = {}
    li1 = sorted(file_list, key=attrgetter(
        'module', 'logic_package', 'package'))
    for m, l in groupby(li1, key=attrgetter("module")):
        logic_package_list = logic_pacakges.get(m, [])
        m_cls_list = list(l)
        for c in m_cls_list:
            update_logic_package(c)
            c.dependencies = [update_logic_package(d) for d in c.dependencies]

        package_dict = {}
        for p, p_cls_list in groupby(m_cls_list, key=attrgetter("logic_package")):
            package_dict[p] = PKG(m, p, list(p_cls_list))

        module_dict[m] = package_dict

    return module_dict


def filter_suspicious_dependency(module_dict):
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            for c in pkg.classes:
                c.suspicious_dependencies = filter(
                    partial(dependency_filter, c), c.dependencies)


def update_usages(class_list, class_map):
    for c in class_list:
        for d in c.dependencies:
            dc = class_map.get(d.path)
            if dc:
                for cat, compiled_re in category_re_dict.items():
                    match = compiled_re.match(dc.path)
                    if match:
                        dep = DEP(c.path, c.name, c.package,
                                  c.module, c.logic_package, cat)
                        break
                dc.usages.append(dep)

                if dependency_filter(dc, dep):
                    dc.suspicious_usages.append(dep)

    for c in class_list:
        c.usages = sorted(c.usages, key=attrgetter(
            "module", "logic_package", "package", "name"))
        c.suspicious_usages = sorted(c.suspicious_usages, key=attrgetter(
            "module", "logic_package", "package", "name"))


if __name__ == "__main__":
    file_list = [c for c in parse_classes_with_dependencies(
        "fast_hub_deps.xml", class_path_filter) if c]

    class_map = dict((c.path, c) for c in file_list)
    update_usages(file_list, class_map)

    module_dict = group_by_modules_and_logic_packages(file_list)
    filter_suspicious_dependency(module_dict)
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            print_package_with_dependencies(pkg, True)
            # for c in pkg.classes:
            #     print_class_with_dependencies(c, True)

    console_markdown(module_dict)
    #console_plant_uml(module_dict)
