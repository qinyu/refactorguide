import xml.etree.ElementTree as ET
import re


class CLS(object):
    """
    Class
    """

    def __init__(self, path, name, package, module):
        self.path = path
        self.name = name
        self.package = package.replace("/", ".")
        self.module = module.replace("/", ":")

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


class DEP(CLS):
    """
    Denpendency
    """

    def __init__(self,  path, name, package, module, category=""):
        CLS.__init__(self, path, name, package, module)
        self.category = category

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


cls_re = re.compile(
    r"(?P<path>^[$]PROJECT_DIR[$][/](?P<module>.*)([/]src[/])(.*[kotlin|java])[/](?P<package>.*)[/](?P<name>.*)[.].*$)")
android_re = re.compile(
    r"(?P<path>.*[/]sdk[/].*[/](?P<module>android-[^\/]*)[/](?P<package>.*)[/](?P<name>.*)[.].*$)")
thirdparty_re = re.compile(
    r"(?P<path>.*[/].gradle[/]caches[/].*files-[^\/]*[/](?P<module>[^\/]*[/][^\/]*[/][^\/]*).*\.jar[!][/](?P<package>.*)[/](?P<name>.*)[.].*$)")
jdk_re = re.compile(
    r"^[$]PROJECT_DIR[$][/](?P<path>(?P<module>.*)([/]src[/])(.*[kotlin|java])[/](?P<package>.*)[/](?P<name>.*)[.].*$)")

def parse_class(file_node):
    return CLS(**cls_re.match(file_node.get("path")).groupdict())


def parse_dependency(dependency_node):
    dep = None
    path = dependency_node.get("path")

    ma = cls_re.match(path)
    if ma:
        dep = DEP(category="Production", **ma.groupdict())

    ma = android_re.match(path)
    if ma:
        dep = DEP(category="Android", **ma.groupdict())

    ma = thirdparty_re.match(path)
    if ma:
        dep = DEP(category="ThirdParty", **ma.groupdict())

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
    all_classes = []
    tree = ET.parse(file_name)
    root = tree.getroot()
    return [parse_class_with_dependencies(f) for f in root.findall("file") if f.get("path").endswith(".kt")]


c_format = '''{}
Class '{name}' in '{package}' belongs to '{module}'
  depends on:
    {}
'''

d_format = "- '{name}' in '{package}' belongs to '{module}'"

if __name__ == "__main__":
    for c in parse_classes_with_dependencies("test_deps.xml"):
        deps_str = [d_format.format(**d.__dict__) for d in c.dependencies]
        print(c_format.format("-"*80, "\n    ".join(deps_str), **c.__dict__))
