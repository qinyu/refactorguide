# coding=utf-8

from config import sorter
from itertools import groupby
from operator import attrgetter


class Statistics(object):

    @property
    def depedencies_statistics(self):
        return len(set([d.module for d in self.dependencies])),\
            len(set([d.logic_package for d in self.dependencies])),\
            len(self.dependencies)

    @property
    def usages_statistics(self):
        return len(set([u.module for u in self.usages])),\
            len(set([u.logic_package for u in self.usages])),\
            len(self.usages)

    @property
    def suspicious_depedencies_statistics(self):
        return len(set([d.module for d in self.suspicious_dependencies])),\
            len(set([d.logic_package for d in self.suspicious_dependencies])),\
            len(self.suspicious_dependencies)

    @property
    def suspicious_usages_statistics(self):
        return len(set([u.module for u in self.suspicious_usages])),\
            len(set([u.logic_package for u in self.suspicious_usages])),\
            len(self.suspicious_usages)

    @property
    def grouped_depedencies(self):
        return grouped_by_modules_and_logic_packages(self.dependencies)

    @property
    def grouped_suspicious_dependencies(self):
        return grouped_by_modules_and_logic_packages(self.suspicious_dependencies)

    @property
    def grouped_usages(self):
        return grouped_by_modules_and_logic_packages(self.usages)

    @property
    def grouped_suspicious_usages(self):
        return grouped_by_modules_and_logic_packages(self.suspicious_usages)


class CLS(Statistics):
    """
    A Java class with all dependencies.

    Attributes
    ----------
    path : str
        full path of java file this class belongs to
    name : str
        name
    package : str
        full package
    logic_package:
        parant package in which classes has some intrinsic logic, package should starts with logic_package.
    module : str
        name of the module this class belongs to
    dependencies : list[DEP]
        list of all using denpendencies, sorted by module, logic_package, package, name

    Methods
    -------
    """

    def __init__(self, path, name, package, module, logic_package=None, dependencies=[]):
        self.path = path
        self.name = name
        self.package = package.replace("/", ".")
        self.logic_package = logic_package if logic_package else self.package
        self.module = module.replace("/", ".").lstrip(".")
        self.dependencies = dependencies
        self.suspicious_dependencies = []
        self.usages = []
        self.suspicious_usages = []
        self.reason = "?"

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, CLS):
            return self.path == other.path
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.path)


class DEP(CLS):
    """
    A dependency used by some class.

    Attributes
    ----------
    category : str
        Such as third party, same product, etc.

    Methods
    -------
    """

    def __init__(self, path, name, package, module, logic_package=None, category=""):
        CLS.__init__(self, path, name, package, module, logic_package)
        self.category = category

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, DEP):
            return self.path == other.path
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.path)


class PKG(Statistics):

    def __init__(self, module,  name, classes):
        self.classes = classes
        self.name = name
        self.module = module

    @property
    def dependencies(self):
        return sorted(set([d for c in self.classes for d in c.dependencies]), key=asorter)

    @property
    def suspicious_dependencies(self):
        return sorted(set([d for c in self.classes for d in c.suspicious_dependencies]), key=sorter)

    @property
    def usages(self):
        return sorted(set([u for c in self.classes for u in c.usages]), key=sorter)

    @property
    def suspicious_usages(self):
        return sorted(set([u for c in self.classes for u in c.suspicious_usages]), key=sorter)


c_format = '''{}
Class '{name}' in '{package}' belongs to '{module}'
  depends on {}:
    {}
  used by {}:
    {}
'''

p_format = '''{}
Package '{name}' belongs to '{module}'
-------
depends on {}:
{}
--------
used by {}:
{}
'''

s_format = "{} mudules {} packages {} classes"

d_format = "- '{name}' in '{package}' belongs to '{module}'"


def grouped_by_modules_and_logic_packages(classes):
    module_dict = {}
    sorted_classes = sorted(classes, key=sorter)
    for m, m_cls_list in groupby(sorted_classes, key=attrgetter("module")):
        package_dict = {}
        for p, p_cls_list in groupby(list(m_cls_list), key=attrgetter("logic_package")):
            package_dict[p] = list(p_cls_list)

        module_dict[m] = package_dict
    return module_dict


def grouped_info(module_dict):
    _str = ""
    for m, pkgs in module_dict.items():
        _str += m + "\n"
        for p, dependencies in pkgs.items():
            _str += "├──" + p + "\n"
            for d in dependencies:
                _str += "│   ├──" + \
                    (d.package + "." + d.name) + "\n"
    return _str


def grouped_dependenies_of(class_or_package, suspicious_only=False):
    module_dict = class_or_package.grouped_suspicious_dependencies if suspicious_only else class_or_package.grouped_dependencies
    return grouped_info(module_dict)


def grouped_usages_of(class_or_package, suspicious_only=False):
    module_dict = class_or_package.grouped_suspicious_usages if suspicious_only else class_or_package.grouped_usages
    return grouped_info(module_dict)


def print_class_with_dependencies(cls, suspicious_only=False):
    deps_str = "\n    ".join([d_format.format(**d.__dict__)
                              for d in (cls.suspicious_dependencies if suspicious_only else cls.dependencies)])
    usages_str = "\n    ".join([d_format.format(**d.__dict__)
                                for d in (cls.suspicious_usages if suspicious_only else cls.usages)])
    deps_stats_str = s_format.format(
        *(cls.suspicious_depedencies_statistics if suspicious_only else cls.depedencies_statistics))
    usages_stats_str = s_format.format(
        *(cls.suspicious_usages_statistics if suspicious_only else cls.usages_statistics))
    print(c_format.format("-"*80,
                          deps_stats_str, deps_str, usages_stats_str, usages_str, **cls.__dict__))


def print_package_with_dependencies(cls, suspicious_only=False):
    deps_str = "\n    ".join([d_format.format(**d.__dict__)
                              for d in (cls.suspicious_dependencies if suspicious_only else cls.dependencies)])
    usages_str = "\n    ".join([d_format.format(**d.__dict__)
                                for d in (cls.suspicious_usages if suspicious_only else cls.usages)])
    deps_stats_str = s_format.format(
        *(cls.suspicious_depedencies_statistics if suspicious_only else cls.depedencies_statistics))
    usages_stats_str = s_format.format(
        *(cls.suspicious_usages_statistics if suspicious_only else cls.usages_statistics))
    print(p_format.format("-"*80,
                          deps_stats_str, deps_str, usages_stats_str, usages_str, **cls.__dict__))


def print_package_with_grouped_dependencies(cls, suspicious_only=False):
    deps_str = grouped_dependenies_of(cls, suspicious_only)
    usages_str = grouped_usages_of(cls, suspicious_only)
    deps_stats_str = s_format.format(
        *(cls.suspicious_depedencies_statistics if suspicious_only else cls.depedencies_statistics))
    usages_stats_str = s_format.format(
        *(cls.suspicious_usages_statistics if suspicious_only else cls.usages_statistics))
    print(p_format.format("-"*80,
                          deps_stats_str, deps_str, usages_stats_str, usages_str, **cls.__dict__))
