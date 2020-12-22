# coding=utf-8

from itertools import groupby
from operator import attrgetter, lshift

sorter = attrgetter('module', 'package', 'raw_package', 'name')


class Component(object):

    @property
    def smell_dependencies(self):
        return [d for d in self.dependencies if d.has_smell]

    @property
    def smell_usages(self):
        return [u for u in self.usages if u.has_smell]

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
    def grouped_dependencies(self):
        return grouped_by_modules_and_packages(self.dependencies)

    @property
    def grouped_smell_dependencies(self):
        return grouped_by_modules_and_packages(self.smell_dependencies)

    @property
    def grouped_usages(self):
        return grouped_by_modules_and_packages(self.usages)

    @property
    def grouped_smell_usages(self):
        return grouped_by_modules_and_packages(self.smell_usages)


class Class(Component):
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

    def __init__(self, path, name, raw_package, module, category="Production", package=None, dependencies=[]):
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

    def oneline_str(self, template):
        return template.format(**self.all_attributes)

    @property
    def all_attributes(self):
        return dict(vars(self), full_name=self.full_name)

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, Class):
            return self.path == other.path
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.path)


class Dependency(Class):
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
        Class.__init__(self, path, name, raw_package,
                       module, category, package)
        self.bad_smells = []

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Dependency):
            return self.path == other.path
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.path)

    def oneline_str(self, template):
        _str = super().oneline_str(template)
        if self.has_smell:
            _str += " (" + "; ".join(
                [bs.description for bs in self.bad_smells]) + ")  "
        return _str

    @property
    def has_smell(self):
        return len(self.bad_smells) > 0


class Package(Component):

    def __init__(self, module, name, classes):
        self.classes = classes
        self.name = name
        self.module = module

    @property
    def dependencies(self):
        return sorted(set([d for c in self.classes for d in c.dependencies]), key=sorter)

    @property
    def smell_dependencies(self):
        return sorted(set([d for c in self.classes for d in c.smell_dependencies]), key=sorter)

    @property
    def usages(self):
        return sorted(set([u for c in self.classes for u in c.usages]), key=sorter)

    @property
    def smell_usages(self):
        return sorted(set([u for c in self.classes for u in c.smell_usages]), key=sorter)

    @property
    def classes(self) -> list[Class]:
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


class Module(Component):

    def __init__(self, name: str, packages: list[Package]):
        self.packages = packages
        self.name = name

    @property
    def classes(self) -> list[Class]:
        return [c for p in self.packages for c in p.classes]

    @property
    def packages(self) -> list[Package]:
        return self._packages

    @packages.setter
    def packages(self, packages: list[Package]):
        self._packages = sorted(packages, key=attrgetter("name"))


def grouped_by_modules_and_packages(classes: list[Class]) -> dict[str:dict[str:Class]]:
    """
    Group class by its attributes: 'module', 'pacakge'(not 'raw_package') and 'name', returns an embeded dict

    >>> sort_by_module = grouped_by_modules_and_packages([Class(path="", name="View", raw_package="should.be.first", module="a"), Class(path="", name="View", raw_package="should.be.second", module="b")])
    >>> print(sort_by_module.keys())
    dict_keys(['a', 'b'])
    >>> print(sort_by_module['a'].keys())
    dict_keys(['should.be.first'])
    >>> print(sort_by_module['b'].keys())
    dict_keys(['should.be.second'])

    >>> sort_by_package = grouped_by_modules_and_packages([Class(path="", name="View", raw_package="should.be.first", module="same.module"), Class(path="", name="View", raw_package="should.be.second", module="same.module")])
    >>> print(sort_by_package.keys())
    dict_keys(['same.module'])
    >>> print(sort_by_package['same.module'].keys())
    dict_keys(['should.be.first', 'should.be.second'])

    >>> sort_by_raw_package = grouped_by_modules_and_packages([Class(path="", name="second", raw_package="same.package.b", module="same.module", package="same.package"), Class(path="", name="first", raw_package="same.package.a", module="same.module", package="same.package")])
    >>> print(sort_by_raw_package.keys())
    dict_keys(['same.module'])
    >>> print(sort_by_raw_package['same.module'].keys())
    dict_keys(['same.package'])
    >>> print([c.name for c in sort_by_raw_package['same.module']['same.package']])
    ['first', 'second']

    >>> sort_by_class = grouped_by_modules_and_packages([Class(path="", name="second", raw_package="same.package", module="same.module"), Class(path="", name="first", raw_package="same.package", module="same.module")])
    >>> print(sort_by_raw_package.keys())
    dict_keys(['same.module'])
    >>> print(sort_by_raw_package['same.module'].keys())
    dict_keys(['same.package'])
    >>> print([c.name for c in sort_by_raw_package['same.module']['same.package']])
    ['first', 'second']
    """
    module_dict = {}
    sorted_classes = sorted(classes, key=sorter)
    for m, m_cls_list in groupby(sorted_classes, key=attrgetter("module")):
        package_dict = {}
        for p, p_cls_list in groupby(list(m_cls_list), key=attrgetter("package")):
            package_dict[p] = list(p_cls_list)

        module_dict[m] = package_dict
    return module_dict


def update_class_logic_packages(class_list: list[Class], logic_pacakges: dict[str:list[str]]):
    """
    Update class' own packge and all its depenedencies' packages and usages' packages

    >>> cls = Class(path="", name="View", raw_package="info.qinyu.biz.ui", module="test")
    >>> cls.dependencies = [Dependency(path="", name="Model", raw_package="info.qinyu.biz.model", module="test", category="Production")]
    >>> cls.usages = [Dependency(path="", name="App", raw_package="info.qinyu", module="test", category="Production"), Dependency(path="", name="Page", raw_package="info.qinyu.biz.ui", module="test", category="Production")]

    # Nothing get updated if empty
    >>> update_class_logic_packages([cls], {})
    >>> print(cls.package)
    info.qinyu.biz.ui
    >>> print(cls.dependencies[0].package)
    info.qinyu.biz.model
    >>> print(cls.usages[0].package)
    info.qinyu
    >>> print(cls.usages[1].package)
    info.qinyu.biz.ui

    >>> update_class_logic_packages([cls], {'test':  ['info.qinyu.biz']})
    >>> print(cls.package)
    info.qinyu.biz
    >>> print(cls.dependencies[0].package)
    info.qinyu.biz
    >>> print(cls.usages[0].package)
    info.qinyu
    >>> print(cls.usages[1].package)
    info.qinyu.biz
    """
    def update(cls):
        for logic_package in logic_pacakges.get(cls.module, []):
            if cls.package.startswith(logic_package):
                cls.package = logic_package
                break
        return cls

    for cls in class_list:
        update(cls)
        cls.dependencies = [update(d) for d in cls.dependencies]
        cls.usages = [update(u) for u in cls.usages]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
