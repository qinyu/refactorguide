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


class PKG(BASE):

    def __init__(self, module,  name, classes):
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


class BadSmell(object):
    def __init__(self, check, description):
        self.check = check
        self.description = description

    def __call__(self, cls, dep):
        return self.check(cls, dep)

    def __str__(self):
        return self.description


class ShouldNotDepend(BadSmell):
    def __init__(self, from_dict, to_dict):
        def check(cls, dep):
            for k, v in from_dict.items():
                if getattr(cls, k) != v:
                    return False
            for k, v in to_dict.items():
                if getattr(dep, k) != v:
                    return False
            return True

        description = "{}不应该依赖{}".format(
            "里的".join(["{}:{}".format(k, v) for k, v in from_dict.items()]),
            "里的".join(["{}:{}".format(k, v) for k, v in to_dict.items()])
        )
        super().__init__(check, description)


c_format = '''{}
{category} Class '{name}' in '{package}' belongs to '{module}'
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

d_format = "- {category} '{name}' in '{package}' belongs to '{module}'"


def grouped_by_modules_and_logic_packages(classes):
    module_dict = {}
    sorted_classes = sorted(classes, key=sorter)
    for m, m_cls_list in groupby(sorted_classes, key=attrgetter("module")):
        package_dict = {}
        for p, p_cls_list in groupby(list(m_cls_list), key=attrgetter("logic_package")):
            package_dict[p] = list(p_cls_list)

        module_dict[m] = package_dict
    return module_dict


def d_format_oneline(d):
    _str = d.package + "." + d.name
    if len(d.bad_smells) > 0:
        _str += " (" + "; ".join(
            [bs.description for bs in d.bad_smells]) + ")  "
    return _str


def deps_format(dependencies, join_str="\n│   ├──", end_str="\n│   └──"):
    d_onelines = [d_format_oneline(d) for d in dependencies]
    return (join_str if len(d_onelines) > 1 else "") + join_str.join(d_onelines[:-1]) + end_str + d_onelines[-1] + "  "


def grouped_info(module_dict):
    _str = ""
    for m, pkgs in module_dict.items():
        _str += m + "  "
        keys = list(pkgs.keys())
        for p in keys[:-1]:
            _str += "\n├──" + p + "  "
            _str += deps_format(pkgs[p])
        _str += "\n└──" + keys[-1] + "  "
        _str += deps_format(pkgs[keys[-1]],
                            join_str="\n    ├──", end_str="\n    └──")
        _str += "\n"
    return _str


def grouped_dependenies_of(class_or_package, suspicious_only=False):
    module_dict = class_or_package.grouped_suspicious_dependencies if suspicious_only else class_or_package.grouped_dependencies
    return grouped_info(module_dict)


def grouped_usages_of(class_or_package, suspicious_only=False):
    module_dict = class_or_package.grouped_suspicious_usages if suspicious_only else class_or_package.grouped_usages
    return grouped_info(module_dict)


def print_class_with_dependencies(cls, suspicious_only=False):
    deps_str = grouped_dependenies_of(cls, suspicious_only)
    usages_str = grouped_usages_of(cls, suspicious_only)
    deps_stats_str = s_format.format(
        *(cls.suspicious_depedencies_statistics if suspicious_only else cls.depedencies_statistics))
    usages_stats_str = s_format.format(
        *(cls.suspicious_usages_statistics if suspicious_only else cls.usages_statistics))
    print(c_format.format("-"*80,
                          deps_stats_str, deps_str, usages_stats_str, usages_str, **cls.__dict__))


def print_package_with_dependencies(cls, suspicious_only=False):
    deps_str = grouped_dependenies_of(cls, suspicious_only)
    usages_str = grouped_usages_of(cls, suspicious_only)
    deps_stats_str = s_format.format(
        *(cls.suspicious_depedencies_statistics if suspicious_only else cls.depedencies_statistics))
    usages_stats_str = s_format.format(
        *(cls.suspicious_usages_statistics if suspicious_only else cls.usages_statistics))
    print(p_format.format("-"*80,
                          deps_stats_str, deps_str, usages_stats_str, usages_str, **cls.__dict__))


pd_format = """
# 包：{}
================================================================================
一共有依赖 {} 项，坏味道依赖 {} 项
一共有调用 {} 处，坏味道调用 {} 处
--------------------------------------------------------------------------------
坏味道依赖最多的3个类，共计{}个坏味道（占比{}），它们是：
{}
--------------------------------------------------------------------------------
坏味道调用最多的3个类，共计{}个坏味道（占比{}），它们是：
{}
--------------------------------------------------------------------------------
"""


def package_description(pkg: PKG):

    def _percenet(sub, total):
        return '{:.2%}'.format(sub/total if total > 0 else 0)

    smell_dependencies_count = len(pkg.suspicious_dependencies)
    smell_usages_count = len(pkg.suspicious_usages)
    top_smell_dependencies_classes = sorted(
        pkg.classes, key=lambda c: len(c.suspicious_dependencies), reverse=True)[:3]
    top_smell_dependencies_count = len(
        set([d for c in top_smell_dependencies_classes for d in c.suspicious_dependencies])) if smell_dependencies_count > 0 else 0
    top_smell_usages_classes = sorted(
        pkg.classes, key=lambda c: len(c.suspicious_usages), reverse=True)[:3]
    top_smell_usages_count = len(
        set([d for c in top_smell_usages_classes for d in c.suspicious_usages])) if smell_usages_count > 0 else 0
    return pd_format.format(
        pkg.name,
        len(pkg.dependencies),
        smell_dependencies_count,
        len(pkg.usages),
        smell_usages_count,
        top_smell_dependencies_count,
        _percenet(top_smell_dependencies_count, smell_dependencies_count),
        "\n".join(
            ["{}（{}）".format(c.full_name, _percenet(len(set(c.suspicious_dependencies)), smell_dependencies_count)) for c in top_smell_dependencies_classes]),
        top_smell_usages_count,
        _percenet(top_smell_usages_count, smell_usages_count),
        "\n".join(
            ["{}（{}）".format(c.full_name, _percenet(len(set(c.suspicious_usages)), smell_usages_count)) for c in top_smell_usages_classes]),
    )
