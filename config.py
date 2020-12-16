# coding = utf-8s
import re

from operator import attrgetter

sorter = attrgetter('module', 'logic_package', 'package', 'name')

category_re_dict = {
    "Production": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/](?P<module>.*)([/]src[/])(.*(kotlin|java))[/](?P<package>.*)[/](?P<name>.*)[.].*$)"),
    "Android": re.compile(
        r"(?P<path>.*[/]sdk[/].*[/](?P<module>android-[^\/]*)([/].*\.jar[!])*[/](?P<package>.*)[/](?P<name>.*)[.].*$)"),
    "ThirdParty": re.compile(
        r"(?P<path>.*[/].gradle[/]caches[/].*files-[^\/]*[/](?P<module>[^\/]*[/][^\/]*[/][^\/]*).*\.jar[!][/](?P<package>.*)[/](?P<name>.*)[.].*$)"),
    "LocalJar": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/](?P<module>.*)([/][^\/]*\.jar[!])[/](?P<package>.*)[/](?P<name>.*)[.].*$)"),
    "JDK": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/](?P<module>.*)([/][^\/]*\.jar[!])[/](?P<package>.*)[/](?P<name>.*)[.].*$)")
}


def class_path_filter(path): return path.endswith("java")


def is_production(dep): return dep.category == "Production"


def smell_cross_module(cls, dep): return is_production(
    dep) and cls.module != dep.module


def smell_cross_package(
    cls, dep): return is_production(
        dep) and cls.module == dep.module and cls.logic_package != dep.logic_package


def smell_cylic_dependency(
    cls, dep): return is_production(
        dep) and cls.path in [u.path for u in cls.usages]


class BadSmell(object):
    def __init__(self, check, description):
        self.check = check
        self.description = description

    def __call__(self, cls, dep):
        return self.check(cls, dep)

    def __str__(self):
        return self.description


dependency_smells = [
    BadSmell(smell_cross_module, "此依赖关系跨模块，需进一步分析"),
    BadSmell(smell_cross_package, "此依赖关系跨包，需进一步分析"),
    BadSmell(smell_cylic_dependency, "此依赖是循环依赖，应当解除")
]

usage_smells = [
    BadSmell(smell_cross_module, "此依赖关系跨模块，需进一步分析"),
    BadSmell(smell_cross_package, "此依赖关系跨包，需进一步分析"),
    BadSmell(smell_cylic_dependency, "此依赖是循环依赖，应当解除")
]


def dependency_filter(cls, dep): return is_production(
    dep) and smell_cross_package(cls, dep)


def usage_filter(cls, usage): return smell_cross_package(usage, cls)


logic_pacakges = {
    # 'app':  ['com.fastaccess.ui.modules']
}
