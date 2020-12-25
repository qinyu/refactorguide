from refactorguide.models import Class, Dependency, Package, grouped_by_modules_and_packages, \
    update_class_logic_packages
import re
import xml.etree.ElementTree as ET

idea_category_dict = {
    "Production": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/]"
        r"(?P<module>.*)([/]src[/])(.*(kotlin|java))[/]"
        r"(?P<raw_package>.*)[/]"
        r"(?P<name>.*)[.].*$)"),
    "Android": re.compile(
        r"(?P<path>.*[/]sdk[/].*[/]"
        r"(?P<module>android-[^\/]*)([/].*\.jar[!])*[/]"
        r"(?P<raw_package>.*)[/]"
        r"(?P<name>.*)[.].*$)"),
    "ThirdParty": re.compile(
        r"(?P<path>.*[/].gradle[/]caches[/].*files-[^\/]*[/]"
        r"(?P<module>[^\/]*[/][^\/]*[/][^\/]*).*\.jar[!][/]"
        r"(?P<raw_package>.*)[/]"
        r"(?P<name>.*)[.].*$)"),
    "LocalJar": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/]"
        r"(?P<module>.*)([/][^\/]*\.jar[!])[/]"
        r"(?P<raw_package>.*)[/]"
        r"(?P<name>.*)[.].*$)"),
    "JDK": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/]"
        r"(?P<module>.*)([/][^\/]*\.jar[!])[/]"
        r"(?P<raw_package>.*)[/]"
        r"(?P<name>.*)[.].*$)")
}


def idea_java_file_filter(
    file_path: str) -> bool: return file_path.endswith("java")


def convert_class_match_dict(_dict):
    """    """
    _dict["raw_package"] = _dict["raw_package"].replace("/", ".")
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
                dep = Dependency(
                    category=cat, **convert_class_match_dict(match.groupdict()))
                break

    # if not dep:
    #     print("Warning: dependency missed %s" % _path)
    return dep


def parse_idea_dependencies(file_node):
    dependencies = [parse_idea_dependency(d)
                    for d in file_node.findall("dependency")]
    return [d for d in dependencies if d]


def update_idea_class_usages(class_list):
    class_map = dict((c.path, c) for c in class_list)

    for u in class_list:
        for d in u.dependencies:
            c = class_map.get(d.path)
            if c:
                usages = c.usages
                for cat, compiled_re in idea_category_dict.items():
                    if compiled_re.match(c.path):
                        usages.append(Dependency(u.path, u.name, u.raw_package,
                                                 u.module, cat, u.package))
                        break
                # 排序
                c.usages = usages


def read_file(idea_dep_file_path, logic_pacakges):
    all_files = ET.parse(idea_dep_file_path).getroot().findall("file")
    all_classes = [parse_idea_class(f) for f in all_files]
    all_classes = [c for c in all_classes if c]
    update_class_logic_packages(all_classes, logic_pacakges)
    update_idea_class_usages(all_classes)

    module_dict = grouped_by_modules_and_packages(all_classes)
    for m, package_dict in module_dict.items():
        for p, p_cls_list in package_dict.items():
            package_dict[p] = Package(m, p, p_cls_list)

    return module_dict
