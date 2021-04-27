from typing import List
from refactorguide.models import Class, Dependency
import re
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

#     "Production"
#     re.compile(
#         r"(?P<path>^[$]PROJECT_DIR[$][/]"
#         r"(?P<module>.*)([/]src[/])(.*(kotlin|java|main))[/]"
#         r"(?P<package>.*)[/]"
#         r"(?P<name>.*)[.](kt|java)$)")
#
#     "Android"
#     re.compile(
#         r"(?P<path>.*[/]sdk[/].*[/]"
#         r"(?P<module>android-[^\/]*)([/].*\.jar[!])*[/]"
#         r"(?P<package>.*)[/]"
#         r"(?P<name>.*)[.].*$)")
#
#     "ThirdParty"
#     re.compile(
#         r"(?P<path>.*[/].gradle[/]caches[/].*files-[^\/]*[/]"
#         r"(?P<module>[^\/]*[/][^\/]*[/][^\/]*).*\.jar[!][/]"
#         r"(?P<package>.*)[/]"
#         r"(?P<name>.*)[.].*$)")
#
#     "LocalJar"
#     re.compile(
#         r"(?P<path>^[$]PROJECT_DIR[$][/]"
#         r"(?P<module>.*)([/][^\/]*\.jar[!])[/]"
#         r"(?P<package>.*)[/]"
#         r"(?P<name>.*)[.].*$)")
#
#     "JDK"
#     re.compile(
#         r"(?P<path>^[$]PROJECT_DIR[$][/]"
#         r"(?P<module>.*)([/][^\/]*\.jar[!])[/]"
#         r"(?P<package>.*)[/]"
#         r"(?P<name>.*)[.].*$)"),

_project_file_path_patterns = [
    re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/]"
        r"(?P<module>.*)([/]src[/])(.*(kotlin|java|main))[/]"
        r"(?P<package>.*)[/]"
        r"(?P<name>.*)[.](kt|java)$)")
]

_dependency_path_patterns = [
    *_project_file_path_patterns,
    re.compile(
        r"(?P<path>.*[/]sdk[/].*[/]"
        r"(?P<module>android-[^\/]*)([/].*\.jar[!])*[/]"
        r"(?P<package>.*)[/]"
        r"(?P<name>.*)[.].*$)")
]


def _find_match_dict(patterns, file_path: str):
    for pattern in patterns:
        match = pattern.match(file_path)
        if match:
            return match.groupdict()
    return None


def _idea_java_file_filter(file_path: str) -> bool: return file_path.endswith("java") or file_path.endswith("kt")


def _convert_match_dict(_dict):
    _dict["package"] = _dict["package"].replace("/", ".")
    _dict["module"] = _dict["module"].replace("/", ".").lstrip(".")
    return _dict


def _parse_idea_class(file_node):
    _path = file_node.get("path")
    match = _find_match_dict(_project_file_path_patterns, _path)
    if match:
        dependencies = [_parse_idea_dependency(d)
                        for d in file_node.findall("dependency")]
        return Class(dependencies=[d for d in dependencies if d], **_convert_match_dict(match))

    if _idea_java_file_filter(_path):
        logger.debug("Can't parse class from %s" % _path)
    return None


def _parse_idea_dependency(dependency_node):
    _path = dependency_node.get("path")

    match = _find_match_dict(_dependency_path_patterns, _path)
    if match:
        return Dependency(layer=None, **_convert_match_dict(match))
    logger.debug("Can't parse dependency from %s" % _path)
    return None


def read_file(idea_dep_file_path) -> List[Class]:
    all_files = ET.parse(idea_dep_file_path).getroot().findall("file")
    all_classes = [_parse_idea_class(f) for f in all_files]
    all_classes = [c for c in all_classes if c]
    return all_classes
