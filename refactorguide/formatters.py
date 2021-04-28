# coding=utf-8

from typing import Dict, List
from refactorguide.models import Class


def _deps_format(dependencies: List[Class], oneline_format: str, join_str: str, end_str: str) -> str:
    d_onelines = [d.oneline_str(oneline_format) for d in dependencies]
    return (join_str if len(d_onelines) > 1 else "") + join_str.join(d_onelines[:-1]) + end_str + d_onelines[-1] + "  "


def dependencies_tree(module_dict: Dict[str, Dict[str, List[Class]]], oneline_format="{full_name}") -> str:
    _str = ""

    for m, pkgs in module_dict.items():
        _str += m + "  "
        keys = list(pkgs.keys())
        for p in keys[:-1]:
            _str += "\n├── " + p + "  "
            _str += _deps_format(pkgs[p], oneline_format,
                                 join_str="\n│   ├── ", end_str="\n│   └── ")
        _str += "\n└── " + keys[-1] + "  "
        _str += _deps_format(pkgs[keys[-1]], oneline_format,
                             join_str="\n    ├──", end_str="\n    └── ")
        _str += "\n"
    return _str
