# coding = utf-8
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


def production_only(dep): return dep.category == "Production"
def cross_module_only(cls, dep): return cls.module != dep.module


def cross_package_only(
    cls, dep): return cls.module != dep.module or cls.logic_package != dep.logic_package


def dependency_filter(cls, dep): return production_only(
    dep) and cross_package_only(cls, dep)


def usage_filter(cls, usage): return cross_package_only(usage, cls)


logic_pacakges = {
    'app':  ['com.fastaccess.ui.modules']
}
