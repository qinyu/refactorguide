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


c_format = '''{}
Class '{name}' in '{package}' belongs to '{module}'
  depends on:
    {}
'''

d_format = "- '{name}' in '{package}' belongs to '{module}'"


def print_class_with_dependencies(cls):
    deps_str = [d_format.format(**d.__dict__) for d in cls.dependencies]
    print(c_format.format("-"*80, "\n    ".join(deps_str), **cls.__dict__))
