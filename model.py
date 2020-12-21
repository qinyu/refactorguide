# coding=utf-8

from itertools import groupby
from operator import attrgetter

sorter = attrgetter('module', 'package', 'raw_package', 'name')


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
            len(set([d.package for d in self.dependencies])),\
            len(self.dependencies)

    @property
    def usages_statistics(self):
        return len(set([u.module for u in self.usages])),\
            len(set([u.package for u in self.usages])),\
            len(self.usages)

    @property
    def suspicious_depedencies_statistics(self):
        return len(set([d.module for d in self.suspicious_dependencies])),\
            len(set([d.package for d in self.suspicious_dependencies])),\
            len(self.suspicious_dependencies)

    @property
    def suspicious_usages_statistics(self):
        return len(set([u.module for u in self.suspicious_usages])),\
            len(set([u.package for u in self.suspicious_usages])),\
            len(self.suspicious_usages)

    @property
    def grouped_dependencies(self):
        return grouped_by_modules_and_packages(self.dependencies)

    @property
    def grouped_suspicious_dependencies(self):
        return grouped_by_modules_and_packages(self.suspicious_dependencies)

    @property
    def grouped_usages(self):
        return grouped_by_modules_and_packages(self.usages)

    @property
    def grouped_suspicious_usages(self):
        return grouped_by_modules_and_packages(self.suspicious_usages)


class CLS(BASE):
    """
    A Java class with all dependencies.

    Attributes
    ----------
    path : str
        full path of java file this class belongs to
    name : str
        name
    raw_package : str
        full package
    ackage:
        parant package in which classes has some intrinsic logic, raw_package should starts with package.
    module : str
        name of the module this class belongs to
    dependencies : list[DEP]
        list of all using denpendencies, sorted by module, raw_package, package, name

    Methods
    -------
    """

    def __init__(self, path, name, raw_package, module, category="Production", package=None,  dependencies=[]):
        self.category = category
        self.path = path
        self.name = name
        self.raw_package = raw_package
        self.package = package if package else self.raw_package
        self.module = module
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
        return "{}.{}".format(self.raw_package, self.name)

    @property
    def logic_name(self):
        return self.full_name[len(self.package):]

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

    def oneline_str(self, template):
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

    def __init__(self, path, name, raw_package, module, category, package=None):
        CLS.__init__(self, path, name, raw_package, module, category, package)
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

    def oneline_str(self, template):
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

    def oneline_str(self, template):
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


def grouped_by_modules_and_packages(classes: list[CLS]) -> dict[str:dict[str:CLS]]:
    module_dict = {}
    sorted_classes = sorted(classes, key=sorter)
    for m, m_cls_list in groupby(sorted_classes, key=attrgetter("module")):
        package_dict = {}
        for p, p_cls_list in groupby(list(m_cls_list), key=attrgetter("package")):
            package_dict[p] = list(p_cls_list)

        module_dict[m] = package_dict
    return module_dict
