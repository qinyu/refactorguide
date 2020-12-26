from typing import List
from refactorguide.models import Class, Dependency
import re
import xml.etree.ElementTree as ET

idea_category_dict = {
    "Production": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/]"
        r"(?P<module>.*)([/]src[/])(.*(kotlin|java))[/]"
        r"(?P<full_name>(?P<package>.*)[/]"
        r"(.*))[.].*$)"),
    "Android": re.compile(
        r"(?P<path>.*[/]sdk[/].*[/]"
        r"(?P<module>android-[^\/]*)([/].*\.jar[!])*[/]"
        r"(?P<full_name>(?P<package>.*)[/]"
        r"(.*))[.].*$)"),
    "ThirdParty": re.compile(
        r"(?P<path>.*[/].gradle[/]caches[/].*files-[^\/]*[/]"
        r"(?P<module>[^\/]*[/][^\/]*[/][^\/]*).*\.jar[!][/]"
        r"(?P<full_name>(?P<package>.*)[/]"
        r"(.*))[.].*$)"),
    "LocalJar": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/]"
        r"(?P<module>.*)([/][^\/]*\.jar[!])[/]"
        r"(?P<full_name>(?P<package>.*)[/]"
        r"(.*))[.].*$)"),
    "JDK": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/]"
        r"(?P<module>.*)([/][^\/]*\.jar[!])[/]"
        r"(?P<full_name>(?P<package>.*)[/]"
        r"(.*))[.].*$)")
}


def idea_java_file_filter(
    file_path: str) -> bool: return file_path.endswith("java")


def convert_class_match_dict(_dict):
    _dict["package"] = _dict["package"].replace("/", ".")
    _dict["module"] = _dict["module"].replace("/", ".").lstrip(".")
    return _dict


def parse_idea_class(file_node):
    path = file_node.get("path")
    match = idea_category_dict["Production"].match(path)
    if match:
        dependencies = [parse_idea_dependency(d)
                        for d in file_node.findall("dependency")]
        return Class(dependencies=[d for d in dependencies if d], **convert_class_match_dict(match.groupdict()))
    # print("Warning: class missed %s" % path)
    return None


def parse_idea_dependency(dependency_node):
    dep = None
    _path = dependency_node.get("path")

    if idea_java_file_filter(_path):
        for cat, compiled_re in idea_category_dict.items():
            match = compiled_re.match(_path)
            if match:
                dep = Dependency(layer=None,
                                 category=cat, **convert_class_match_dict(match.groupdict()))
                break

    # if not dep:
    #     print("Warning: dependency missed %s" % _path)
    return dep


def parse_idea_dependencies(file_node):
    dependencies = [parse_idea_dependency(d)
                    for d in file_node.findall("dependency")]
    return [d for d in dependencies if d]


def read_file(idea_dep_file_path) -> List[Class]:
    all_files = ET.parse(idea_dep_file_path).getroot().findall("file")
    all_classes = [parse_idea_class(f) for f in all_files]
    all_classes = [c for c in all_classes if c]
    return all_classes
