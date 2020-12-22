# coding=utf-8

from model import CLS, PKG


pd_format = """
# 包：{}
================================================================================
一共有依赖 {} 项，坏味道依赖 {} 项
一共有调用 {} 处，坏味道调用 {} 处
--------------------------------------------------------------------------------
坏味道依赖最多的{}个类，共计{}个坏味道（占比{}），它们是：
{}
--------------------------------------------------------------------------------
坏味道调用最多的{}个类，共计{}个坏味道（占比{}），它们是：
{}
--------------------------------------------------------------------------------
"""


def package_description(pkg: PKG, top=3, oneline_format="{full_name}") -> str:

    def _percenet(sub, total):
        return '{:.2%}'.format(sub/total if total > 0 else 0)

    smell_dependencies_count = len(pkg.suspicious_dependencies)
    smell_usages_count = len(pkg.suspicious_usages)
    smell_dependencies_classes = sorted(
        pkg.classes, key=lambda c: len(c.suspicious_dependencies), reverse=True)
    top_smell_dependencies_classes = smell_dependencies_classes[:top] if len(
        smell_dependencies_classes) > top else smell_dependencies_classes
    top_smell_dependencies_count = len(
        set([d for c in top_smell_dependencies_classes for d in c.suspicious_dependencies])) if smell_dependencies_count > 0 else 0
    smell_usages_classes = sorted(
        pkg.classes, key=lambda c: len(c.suspicious_usages), reverse=True)
    top_smell_usages_classes = smell_usages_classes[:top] if len(
        smell_usages_classes) > top else smell_usages_classes
    top_smell_usages_count = len(
        set([d for c in top_smell_usages_classes for d in c.suspicious_usages])) if smell_usages_count > 0 else 0
    return pd_format.format(
        pkg.name,
        len(pkg.dependencies),
        smell_dependencies_count,
        len(pkg.usages),
        smell_usages_count,
        top,
        top_smell_dependencies_count,
        _percenet(top_smell_dependencies_count, smell_dependencies_count),
        "\n".join(
            ["{}（{}）".format(c.oneline_str(oneline_format), _percenet(len(set(c.suspicious_dependencies)), smell_dependencies_count)) for c in top_smell_dependencies_classes]),
        top,
        top_smell_usages_count,
        _percenet(top_smell_usages_count, smell_usages_count),
        "\n".join(
            ["{}（{}）".format(c.oneline_str(oneline_format), _percenet(len(set(c.suspicious_usages)), smell_usages_count)) for c in top_smell_usages_classes]),
    )


cd_format = """
# 类：{}
================================================================================
一共有依赖 {} 项，坏味道依赖 {} 项
一共有调用 {} 处，坏味道调用 {} 处
--------------------------------------------------------------------------------
"""


def class_description(cls: CLS) -> str:
    smell_dependencies_count = len(cls.suspicious_dependencies)
    smell_usages_count = len(cls.suspicious_usages)
    return cd_format.format(
        cls.full_name,
        len(cls.dependencies),
        smell_dependencies_count,
        len(cls.usages),
        smell_usages_count,
    )


def deps_format(dependencies: list[CLS], oneline_format: str, join_str: str, end_str: str) -> str:
    d_onelines = [d.oneline_str(oneline_format) for d in dependencies]
    return (join_str if len(d_onelines) > 1 else "") + join_str.join(d_onelines[:-1]) + end_str + d_onelines[-1] + "  "


def dependencies_tree_description(module_dict: dict[str:dict[str:CLS]], oneline_format="{full_name}") -> str:
    _str = ""

    for m, pkgs in module_dict.items():
        _str += m + "  "
        keys = list(pkgs.keys())
        for p in keys[:-1]:
            _str += "\n├──" + p + "  "
            _str += deps_format(pkgs[p], oneline_format,
                                join_str="\n│   ├──", end_str="\n│   └──")
        _str += "\n└──" + keys[-1] + "  "
        _str += deps_format(pkgs[keys[-1]], oneline_format,
                            join_str="\n    ├──", end_str="\n    └──")
        _str += "\n"
    return _str