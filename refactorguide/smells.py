# coding=utf-8

from refactorguide.models import Class, Hierarchy


class Smell(object):
    def __init__(self, check, description):
        self.check = check
        self.description = description

    def __call__(self, cls, dep):
        return self.check(cls, dep)

    def __str__(self):
        return self.description

    @property
    def all_args(self):
        return None


class SmellDependency(Smell):

    def __init__(self, **kwargs):
        self.from_dict = kwargs["from"]
        self.to_dict = kwargs["to"]

        def check(cls: Class, dep: Class):
            return cls.wildcards_macth(**self.from_dict) and dep.wildcards_macth(**self.to_dict)

        description = "{} shouldn't depends {} from".format(
            "'s ".join(["{}'{}'".format(k, v)
                        for k, v in self.from_dict.items()]),
            "'s ".join(["{}'{}'".format(k, v)
                        for k, v in self.to_dict.items()])
        )
        super().__init__(check, description)

    @ property
    def all_args(self):
        return {"from": self.from_dict, "to": self.to_dict}


def smell_cross_module(
    cls: Class, dep: Class) -> bool: return dep.is_production and cls.module != dep.module


def smell_cross_package(
    cls, dep): return dep.is_production and cls.module == dep.module and cls.package != dep.package


def smell_cylic_dependency(cls, dep):
    if type(cls) == Class:
        return dep.is_production and dep.path in [u.path for u in cls.usages]
    elif type(dep) == Class:
        return cls.is_production and cls.path in [u.path for u in dep.usages]


class SmellDependencyCrossModule(Smell):
    def __init__(self) -> None:
        super().__init__(smell_cross_module, "此依赖关系跨模块，需进一步分析")


class SmellDependencyCrossPackage(Smell):
    def __init__(self) -> None:
        super().__init__(smell_cross_package, "此依赖关系跨包，需进一步分析")


class SmellCylicDependency(Smell):
    def __init__(self) -> None:
        super().__init__(smell_cylic_dependency, "此依赖是循环依赖，应当解除")


# def is_layer(cls: Class, layer):
#     for w in design.LAYERS[layer]:
#         if cls.wildcards_macth(**w):
#             return True
#     return False


class SmellLayerDependency(Smell):
    def __init__(self, **kwargs):
        self.from_layer = kwargs["from"]
        self.to_layer = kwargs["to"]

        def check(cls: Class, dep: Class):
            return cls.is_layer(self.from_layer) and dep.is_layer(self.to_layer)

        description = "'{}' layer shouldn't depend on '{}' layer".format(
            self.from_layer, self.to_layer)
        super().__init__(check, description)


def find_smells(hierarchy: Hierarchy, dependency_smells):
    for c in hierarchy.classes:
        for d in [d for d in c.dependencies if d.is_production]:
            for smell in dependency_smells:
                if smell(c, d):
                    d.bad_smells.append(smell)
        for u in [u for u in c.usages if u.is_production]:
            for smell in dependency_smells:
                if smell(u, c):
                    u.bad_smells.append(smell)
