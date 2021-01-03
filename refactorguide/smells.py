# coding=utf-8

from refactorguide.models import Class, Hierarchy, to_wd_dict


class Smell(object):
    def __init__(self, check, description):
        self.check = check
        self.description = description

    def __call__(self, hierachy, cls, dep):
        return self.check(hierachy, cls, dep)

    def __str__(self):
        return self.description

    @property
    def all_args(self):
        return None


class SmellDependency(Smell):

    def __init__(self, **kwargs):
        self.from_dict = to_wd_dict(kwargs["from"])
        self.to_dict = to_wd_dict(kwargs["to"])

        def check(hierachy, cls: Class, dep: Class):
            return cls.path_match(**self.from_dict) and dep.path_match(**self.to_dict)

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


def smell_cross_module(hierachy,
                       cls: Class, dep: Class) -> bool: return dep.is_production and cls.module != dep.module


def smell_cross_package(hierachy,
                        cls, dep): return dep.is_production and cls.module == dep.module and cls.package != dep.package


def smell_cylic_dependency(hierachy, cls, dep):
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


def find_smells(hierarchy: Hierarchy, dependency_smells):
    for c in hierarchy.classes:
        for d in [d for d in c.dependencies if d.is_production]:
            for smell in dependency_smells:
                if smell(hierarchy, c, d):
                    d.bad_smells.append(smell)
        for u in [u for u in c.usages if u.is_production]:
            for smell in dependency_smells:
                if smell(hierarchy, u, c):
                    u.bad_smells.append(smell)
