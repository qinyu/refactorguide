# coding=utf-8

from itertools import groupby
from operator import attrgetter

sorter = attrgetter('module', 'logic_package', 'package', 'name')


class BASE(object):

    @property
    def suspicious_dependencies(self):
        return [d for d in self.dependencies if len(d.bad_smells) > 0]

    @property
    def suspicious_usages(self):
        return [u for u in self.usages if len(u.bad_smells) > 0]

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
    def grouped_dependencies(self):
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


class CLS(BASE):
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

    def __init__(self, path, name, package, module, category="Production", logic_package=None,  dependencies=[]):
        self.category = category
        self.path = path
        self.name = name
        self.package = package.replace("/", ".")
        self.logic_package = logic_package if logic_package else self.package
        self.module = module.replace("/", ".").lstrip(".")
        self.dependencies = dependencies
        self.usages = []

    @property
    def dependencies(self):
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies):
        self._dependencies = sorted(dependencies, key=sorter)

    @property
    def usages(self):
        return self._usages

    @usages.setter
    def usages(self, usages):
        self._usages = sorted(usages, key=sorter)

    @property
    def full_name(self):
        return "{}.{}".format(self.package, self.name)

    @property
    def logic_name(self):
        return self.full_name[:len(self.logic_package)]

    @property
    def is_production(self):
        return self.category == "Production"

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

    def oneline_str(self, template="{full_name}"):
        return template.format(**self.all_attributes)

    @property
    def all_attributes(self):
        return dict(vars(self), full_name=self.full_name)


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

    def __init__(self, path, name, package, module, category, logic_package=None):
        CLS.__init__(self, path, name, package,
                     module, category, logic_package)
        self.bad_smells = []

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

    def oneline_str(self, template="{full_name}"):
        _str = super().oneline_str(template)
        if len(self.bad_smells) > 0:
            _str += " (" + "; ".join(
                [bs.description for bs in self.bad_smells]) + ")  "
        return _str


class PKG(BASE):

    def __init__(self, module, name, classes):
        self.classes = classes
        self.name = name
        self.module = module

    @property
    def dependencies(self):
        return sorted(set([d for c in self.classes for d in c.dependencies]), key=sorter)

    @property
    def suspicious_dependencies(self):
        return sorted(set([d for c in self.classes for d in c.suspicious_dependencies]), key=sorter)

    @property
    def usages(self):
        return sorted(set([u for c in self.classes for u in c.usages]), key=sorter)

    @property
    def suspicious_usages(self):
        return sorted(set([u for c in self.classes for u in c.suspicious_usages]), key=sorter)

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, classes):
        self._classes = sorted(classes, key=sorter)

    @property
    def full_name(self):
        return self.name

    def oneline_str(self, template="{full_name}"):
        return template.format(**self.all_attributes)

    @property
    def all_attributes(self):
        return dict(vars(self), full_name=self.full_name)


class MOD(BASE):

    def __init__(self, name, classes):
        self.packages = classes
        self.name = name

    @property
    def dependencies(self):
        return sorted(set([d for pkg in self.packages for d in pkg.dependencies]), key=sorter)

    @property
    def suspicious_dependencies(self):
        return sorted(set([d for pkg in self.packages for d in pkg.suspicious_dependencies]), key=sorter)

    @property
    def usages(self):
        return sorted(set([u for pkg in self.packages for u in pkg.usages]), key=sorter)

    @property
    def suspicious_usages(self):
        return sorted(set([u for pkg in self.packages for u in pkg.suspicious_usages]), key=sorter)

    @property
    def packages(self):
        return self._packages

    @packages.setter
    def packages(self, packages):
        self._packages = sorted(packages, key=attrgetter("name"))


def grouped_by_modules_and_logic_packages(classes):
    module_dict = {}
    sorted_classes = sorted(classes, key=sorter)
    for m, m_cls_list in groupby(sorted_classes, key=attrgetter("module")):
        package_dict = {}
        for p, p_cls_list in groupby(list(m_cls_list), key=attrgetter("logic_package")):
            package_dict[p] = list(p_cls_list)

        module_dict[m] = package_dict
    return module_dict


def deps_format(dependencies: list[DEP], oneline_format, join_str, end_str):
    d_onelines = [d.oneline_str(oneline_format) for d in dependencies]
    return (join_str if len(d_onelines) > 1 else "") + join_str.join(d_onelines[:-1]) + end_str + d_onelines[-1] + "  "


def grouped_info(module_dict, oneline_format="{full_name}"):
    _str = ""

    for m, pkgs in module_dict.items():
        _str += m + "  "
        keys = list(pkgs.keys())
        for p in keys[:-1]:
            _str += "\n├──" + p + "  "
            _str += deps_format(pkgs[p], oneline_format,
                                join_str="\n│   ├──", end_str="\n│   └──")
        _str += "\n└──" + keys[-1] + "  "
        _str += deps_format(pkgs[keys[-1]], oneline_format,
                            join_str="\n    ├──", end_str="\n    └──")
        _str += "\n"
    return _str


def grouped_dependenies_of(class_or_package: BASE, suspicious_only=False):
    module_dict = class_or_package.grouped_suspicious_dependencies if suspicious_only else class_or_package.grouped_dependencies
    return grouped_info(module_dict)


def grouped_usages_of(class_or_package, suspicious_only=False):
    module_dict = class_or_package.grouped_suspicious_usages if suspicious_only else class_or_package.grouped_usages
    return grouped_info(module_dict)


# def print_class_with_dependencies(cls, suspicious_only=False):
#     deps_str = grouped_dependenies_of(cls, suspicious_only)
#     usages_str = grouped_usages_of(cls, suspicious_only)
#     deps_stats_str = s_format.format(
#         *(cls.suspicious_depedencies_statistics if suspicious_only else cls.depedencies_statistics))
#     usages_stats_str = s_format.format(
#         *(cls.suspicious_usages_statistics if suspicious_only else cls.usages_statistics))
#     print(c_format.format("-"*80,
#                           deps_stats_str, deps_str, usages_stats_str, usages_str, **cls.__dict__))


# def print_package_with_dependencies(cls, suspicious_only=False):
#     deps_str = grouped_dependenies_of(cls, suspicious_only)
#     usages_str = grouped_usages_of(cls, suspicious_only)
#     deps_stats_str = s_format.format(
#         *(cls.suspicious_depedencies_statistics if suspicious_only else cls.depedencies_statistics))
#     usages_stats_str = s_format.format(
#         *(cls.suspicious_usages_statistics if suspicious_only else cls.usages_statistics))
#     print(p_format.format("-"*80,
#                           deps_stats_str, deps_str, usages_stats_str, usages_str, **cls.__dict__))
