import xml.etree.ElementTree as ET
import re
from config import category_re_dict, ext
from model import CLS, DEP, print_class_with_dependencies
from uml import console_plant_uml
from statistics import console_statistics_data

def parse_class(file_node):
    return CLS(**category_re_dict["Production"].match(file_node.get("path")).groupdict())


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
    return [parse_dependency(d) for d in file_node.findall("dependency")]


def parse_class_with_dependencies(file_node):
    cls = parse_class(file_node)
    cls.dependencies = [d for d in parse_dependencies(file_node) if d]
    return cls


def parse_classes_with_dependencies(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    return [parse_class_with_dependencies(f) for f in root.findall("file") if f.get("path").endswith(ext)]


c_format = '''{}
Class '{name}' in '{package}' belongs to '{module}'
  depends on:
    {}
'''

d_format = "- '{name}' in '{package}' belongs to '{module}'"

if __name__ == "__main__":
    file_list=parse_classes_with_dependencies("test_deps.xml")
    for c in file_list:
        print_class_with_dependencies(c)
    console_plant_uml(file_list)
    console_statistics_data(file_list)
    