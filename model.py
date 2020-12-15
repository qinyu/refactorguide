class CLS(object):
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
        self.module = module.replace("/", ":")
        self.dependencies = dependencies
        self.suspicious_dependencies = []
        self.usages = []
        self.suspicious_usages = []

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__

    def depedencies_statistics(self):
        return len(set([d.module for d in self.dependencies])), len(set([d.logic_package for d in self.dependencies])), len(self.dependencies)

    def usages_statistics(self):
        return len(set([d.module for d in self.usages])), len(set([d.logic_package for d in self.usages])), len(self.usages)

    def suspicious_depedencies_statistics(self):
        return len(set([d.module for d in self.suspicious_dependencies])), len(set([d.logic_package for d in self.suspicious_dependencies])), len(self.suspicious_dependencies)

    def suspicious_usages_statistics(self):
        return len(set([d.module for d in self.suspicious_usages])), len(set([d.logic_package for d in self.suspicious_usages])), len(self.suspicious_usages)


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

    def __init__(self,  path, name, package, module, logic_package=None, category=""):
        CLS.__init__(self, path, name, package, module, logic_package)
        self.category = category

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


c_format = '''{}
Class '{name}' in '{package}' belongs to '{module}'
  depends on {}:
    {}
  used by {}:
    {}
'''

s_format = "{} mudules {} packages {} classes"

d_format = "- '{name}' in '{package}' belongs to '{module}'"


def print_class_with_dependencies(cls, suspicious_only=False):
    deps_str = "\n    ".join([d_format.format(**d.__dict__)
                              for d in (cls.suspicious_dependencies if suspicious_only else cls.dependencies)])
    usages_str = "\n    ".join([d_format.format(**d.__dict__)
                                for d in (cls.suspicious_usages if suspicious_only else cls.usages)])
    deps_stats_str = s_format.format(
        *(cls.suspicious_depedencies_statistics() if suspicious_only else cls.depedencies_statistics()))
    usages_stats_str = s_format.format(
        *(cls.suspicious_usages_statistics() if suspicious_only else cls.usages_statistics()))
    print(c_format.format("-"*80,
                           deps_stats_str, deps_str, usages_stats_str, usages_str, **cls.__dict__))
