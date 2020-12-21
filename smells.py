# coding=utf-8

from model import CLS, PKG


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
            "里的".join(["{}:{}".format(k, v)
                       for k, v in from_dict.items()]),
            "里的".join(["{}:{}".format(k, v) for k, v in to_dict.items()])
        )
        super().__init__(check, description)


def smell_cross_module(
    cls: CLS, dep: CLS) -> bool: return dep.is_production and cls.module != dep.module


def smell_cross_package(
    cls, dep): return dep.is_production and cls.module == dep.module and cls.logic_package != dep.logic_package


def smell_cylic_dependency(
    cls, dep): return dep.is_production and cls.path in [u.path for u in cls.usages]


class BadSmellCrossModule(BadSmell):
    def __init__(self) -> None:
        super().__init__(smell_cross_module, "此依赖关系跨模块，需进一步分析")


class BadSmellCrossPackage(BadSmell):
    def __init__(self) -> None:
        super().__init__(smell_cross_module, "此依赖关系跨模块，需进一步分析")


class BadSmellCylicDependency(BadSmell):
    def __init__(self) -> None:
        super().__init__(smell_cylic_dependency, "此依赖是循环依赖，应当解除")


def find_smells(module_dict: dict[str:dict[str:PKG]], dependency_smells, usage_smells):
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            for c in pkg.classes:
                for d in [d for d in c.dependencies if d.is_production]:
                    for smell in dependency_smells:
                        if smell(c, d):
                            d.bad_smells.append(smell)
                for u in [u for u in c.usages if u.is_production]:
                    for smell in usage_smells:
                        if smell(u, c):
                            u.bad_smells.append(smell)
