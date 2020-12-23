# coding = utf-8s
from configparser import ConfigParser as CP
import io
import json
from refactorguide.smells import Smell, SmellDependency, SmellDependencyCrossModule, \
    SmellDependencyCrossPackage, SmellCylicDependency
from itertools import groupby

from typing import List, Dict


exmaple_layers = {
    "application": [],
    "business": [{"module": "In_this_module", "package": "in.this.packqge",
                  "name": "OnlyThisClassBelongsToBusinessLayer"}],
    "service":  [
        {"module": "Whole_module_belongs_to_service_layer"}
    ],
    "platform":  [
        {"module": "In_this_module",
            "package": "only.this.package.belongs.to.platform.layer"}
    ]
}

example_logic_pacakges = {
    'InThisModule':  ['all.sub.packages.in.this.package.should.be.consideres.as.whole'],
    'InAnotherModule':  ['you.can.set', 'multiple.packages']
}

example_bad_smells = [
    SmellDependencyCrossModule(),
    SmellDependencyCrossPackage(),
    SmellCylicDependency(),
    SmellDependency(**{
        'from': {'module': 'OneModule'},
        'to': {'module': 'AnotherModule'}
    }),
    SmellDependency(**{
        'from': {'module': 'OneModule'},
        'to': {'package': 'one.package', 'module': 'InAnotherModule'}
    }),
    SmellDependency(**{
        'from': {'module': 'OneModule'},
        'to': {'name': 'OneClass', 'package': 'in.one.package', 'module': 'InAnsotherModule'}
    })
]


def read_logic_pacakges(cp: CP) -> Dict[str, List[str]]:
    """
    >>> sample_config = '''
    ... [logic packages]
    ...   app: ["com.pretty.helper",
    ...     "com.data.dao.converters"]
    ...   Test: ["com.pretty.helper.test"]
    ... '''
    >>> cp = CP(allow_no_value=True)
    >>> cp.optionxform = str
    >>> cp.read_string(sample_config)
    >>> logic_packages = read_logic_pacakges(cp)
    >>> print(logic_packages)
    {'app': ['com.pretty.helper', 'com.data.dao.converters'], 'Test': ['com.pretty.helper.test']}
    """
    logic_pacakges = {}
    if cp.has_section('logic packages'):
        for m, packages_json in cp.items('logic packages'):
            if packages_json:
                logic_pacakges[m] = json.loads(packages_json)
            else:
                print("Warning: no packages specified in {}".format(m))
    return logic_pacakges


def write_logic_packages(cp: CP, logic_pacakges: Dict[str, List[str]] = example_logic_pacakges):
    _section = "logic pacakges"
    cp.add_section(_section)
    cp.set(_section,
           "; Uncomment following exmaple and replace with your cohesive packages in each module. ")

    for module, packages in logic_pacakges.items():
        cp.set(_section, module, json.dumps(packages, indent=2))


def read_bad_smells(cp: CP) -> List[Smell]:
    """
    >>> sample_config = '''
    ... [bad smells]
    ...   SmellDependencyCrossModule
    ...   SmellDependencyCrossPackage
    ...   SmellCylicDependency
    ...   SmellDependency: [
    ...       {
    ...         "from": {"module": "app", "package": "com.pretty.helper" },
    ...        "to": {"module": "app", "package": "com.data.dao", "name": "NameParser"}
    ...       }
    ...     ]
    ... '''
    >>> cp = CP(allow_no_value=True)
    >>> cp.optionxform = str
    >>> cp.read_string(sample_config)
    >>> bad_smells = read_bad_smells(cp)
    >>> print([type(s).__name__ for s in bad_smells])
    ['SmellDependencyCrossModule', 'SmellDependencyCrossPackage', 'SmellCylicDependency', 'SmellDependency']
    """
    module = __import__("refactorguide.smells")
    bad_smells = []
    if cp.has_section('bad smells'):
        for smell_name, params_json in cp.items('bad smells'):
            if params_json:
                smell_class_ = getattr(module, smell_name)
                for params in json.loads(params_json):
                    bad_smells.append(smell_class_(**params))
            else:
                smell_class_ = getattr(module, smell_name)
                bad_smells.append(smell_class_())
    return bad_smells


def write_bad_smells(cp: CP, bad_smells: List[Smell] = example_bad_smells):
    def sorter(bs): return type(bs).__name__
    cp.add_section("bad smells")
    cp.set(
        "bad smells", "; Uncomment following smells and replace with your rules ")
    for t, bs_list in groupby(sorted(bad_smells, key=sorter), key=sorter):
        args_list = [bs.all_args for bs in bs_list if bs.all_args]
        cp.set("bad smells", t, json.dumps(
            args_list, indent=2) if len(args_list) > 0 else None)


def read_layers(cp: CP) -> Dict[str, List[Dict[str, str]]]:
    """
    >>> sample_config = '''
    ... [layers]
    ...   platform = [
    ...       { "module": "app", "package": "com.pretty.helper" }
    ...     ]
    ... '''
    >>> config = CP(allow_no_value=True)
    >>> config.optionxform = str
    >>> config.read_string(sample_config)
    >>> layers = read_layers(config)
    >>> print(layers)
    {'platform': [{'module': 'app', 'package': 'com.pretty.helper'}]}
    """
    layers = {}
    if cp.has_section('layers'):
        for layer_name, _json in cp.items('layers'):
            layers[layer_name] = json.loads(_json)
    return layers


def write_layers(cp: CP, layers: Dict[str, List[Dict[str, str]]] = exmaple_layers):
    cp.add_section("layers")
    cp.set("layers", "; Desired layers")
    for k, v in layers.items():
        cp.set("layers", k, json.dumps(v, indent=2))


def write_example_config(cp: CP, file_path: str):
    write_logic_packages(cp)
    write_layers(cp)
    write_bad_smells(cp)

    lines = ""
    with io.StringIO() as ss:
        cp.write(ss)
        ss.seek(0)
        lines = "".join([('; ' if not line.startswith(
            "[") else '') + line for line in ss.readlines()])

    with open(file_path, 'w', encoding="utf-8") as configfile:
        configfile.writelines(lines)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
