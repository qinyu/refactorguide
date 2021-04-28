# coding=utf-8

from refactorguide.models import Class, Hierarchy, path_to_wd_dict, wd_dict_to_path


class Smell(object):
    def __init__(self, check, description):
        self.check = check
        self.description = description

    def __call__(self, hierachy, cls, dep):
        return self.check(hierachy, cls, dep)

    @property
    def all_args(self):
        return {}

    def __str__(self):
        return type(self).__name__ + "" + str(self.all_args)


class SmellDependency(Smell):

    def __init__(self, **kwargs):
        self.from_dict = path_to_wd_dict(kwargs["from"])
        self.to_dict = path_to_wd_dict(kwargs["to"])

        def check(hierachy, cls: Class, dep: Class):
            return cls.is_production and dep.is_production and \
                cls.path_match(**self.from_dict) and dep.path_match(**self.to_dict)

        description = "{} 不应该依赖 {}".format(
            "'s ".join(["{} '{}'".format(k, v)
                        for k, v in self.from_dict.items()]),
            "'s ".join(["{} '{}'".format(k, v)
                        for k, v in self.to_dict.items()])
        )
        super().__init__(check, description)

    @property
    def all_args(self):
        return {"from": wd_dict_to_path(self.from_dict),
                "to": wd_dict_to_path(self.to_dict)}

    def __eq__(self, other):
        if isinstance(other, SmellDependency):
            return self.all_args == other.all_args
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__str__())


def cross_module(hierachy,
                 cls: Class, dep: Class) -> bool: return cls.is_production and dep.is_production and\
    cls.module != dep.module


def cross_package(hierachy,
                  cls, dep): return cls.is_production and dep.is_production and \
    cls.module == dep.module and cls.package != dep.package


def cylic_dependency(hierachy, cls, dep):
    if type(cls) == Class:
        return cls.is_production and dep.is_production and dep.path in [u.path for u in cls.usages]
    elif type(dep) == Class:
        return cls.is_production and dep.is_production and cls.path in [u.path for u in dep.usages]


def addon_dependency(hierachy, cls, dep):
    return cls.is_production and not dep.is_production


class SmellDependencyCrossModule(Smell):
    def __init__(self) -> None:
        super().__init__(cross_module, "此依赖关系跨模块，需进一步分析")

    def __eq__(self, other):
        if isinstance(other, SmellDependencyCrossModule):
            return self.all_args == other.all_args
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__str__())


class SmellDependencyCrossPackage(Smell):
    def __init__(self) -> None:
        super().__init__(cross_package, "此依赖关系跨包，需进一步分析")

    def __eq__(self, other):
        if isinstance(other, SmellDependencyCrossPackage):
            return self.all_args == other.all_args
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__str__())


class SmellCylicDependency(Smell):
    def __init__(self) -> None:
        super().__init__(cylic_dependency, "此依赖是循环依赖，应当解除")

    def __eq__(self, other):
        if isinstance(other, SmellCylicDependency):
            return self.all_args == other.all_args
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__str__())


class SmellAddOnDependency(Smell):
    def __init__(self, **kwargs):
        self.addon_dict = path_to_wd_dict(kwargs)

        def check(hierachy, cls: Class, dep: Class):
            return cls.is_production and not dep.is_production and \
                dep.path_match(ignore_none=True, **self.addon_dict)

        description = "不应该依赖系统接口"
        super().__init__(check, description)

    def __eq__(self, other):
        if isinstance(other, SmellAddOnDependency):
            return self.all_args == other.all_args
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__str__())

    @property
    def all_args(self):
        return self.addon_dict


def find_smells(hierarchy: Hierarchy, dependency_smells):
    for c in hierarchy.classes:
        for d in [d for d in c.dependencies]:
            for smell in dependency_smells:
                if smell(hierarchy, c, d):
                    d.bad_smells.append(smell)
        # for u in [u for u in c.usages]:
        #     for smell in dependency_smells:
        #         if smell(hierarchy, u, c):
        #             u.bad_smells.append(smell)
