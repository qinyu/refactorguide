class CLS(object):
    """
    Class
    """

    def __init__(self, path, name, package, module, dependencies=[]):
        self.path = path
        self.name = name
        self.package = package.replace("/", ".")
        self.logic_package = self.package
        self.module = module.replace("/", ":")
        self.dependencies = dependencies
        self.suspicious_dependencies = []

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


c_format = '''{}
Class '{name}' in '{package}' belongs to '{module}'
  depends on:
    {}
'''

d_format = "- '{name}' in '{package}' belongs to '{module}'"


def print_class_with_dependencies(cls, suspicious_dependencies_only=False):
    deps_str = [d_format.format(**d.__dict__)
                for d in (cls.suspicious_dependencies if suspicious_dependencies_only else cls.dependencies)]
    print(c_format.format("-"*80, "\n    ".join(deps_str), **cls.__dict__))
