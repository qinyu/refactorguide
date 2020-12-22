# coding = utf-8s
import configparser
import io
import json
from smells import BadSmell, ShouldNotDepend, BadSmellCrossModule, BadSmellCrossPackage, BadSmellCylicDependency
from itertools import groupby


exmaple_layers = {
    "application": [],
    "business": [{"module": "In_this_module", "package": "and.in.this.packqge",
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
    BadSmellCrossModule(),
    BadSmellCrossPackage(),
    BadSmellCylicDependency(),
    ShouldNotDepend(
        {'module': 'OneModule'},
        {'module': 'AnotherModule'}
    ),
    ShouldNotDepend(
        {'module': 'OneModule'},
        {'package': 'one.package', 'module': 'InAnotherModule'}
    ),
    ShouldNotDepend(
        {'module': 'OneModule'},
        {'name': 'OneClass', 'package': 'in.one.package', 'module': 'InAnotherModule'}
    )
]


def read_logic_pacakges(config: configparser.ConfigParser) -> dict[str:list[str]]:
    """
    >>> sample_config = '''
    ... [logic packages]
    ...   app: ["com.prettifier.pretty.helper",
    ...     "com.fastaccess.data.dao.converters"]
    ...   Test: ["com.prettifier.pretty.helper.test"]
    ... '''
    >>> config = configparser.ConfigParser(allow_no_value=True)
    >>> config.optionxform = str
    >>> config.read_string(sample_config)
    >>> logic_packages = read_logic_pacakges(config)
    >>> print(logic_packages)
    {'app': ['com.prettifier.pretty.helper', 'com.fastaccess.data.dao.converters'], 'Test': ['com.prettifier.pretty.helper.test']}
    """
    logic_pacakges = {}
    if config.has_section('logic packages'):
        for m, packages_json in config.items('logic packages'):
            if packages_json:
                logic_pacakges[m] = json.loads(packages_json)
            else:
                print("Warning: no packages specified in {}".format(m))
    return logic_pacakges


def write_logic_packages(config: configparser.ConfigParser, logic_pacakges: dict[str:list[str]] = example_logic_pacakges):
    config.add_section("logic pacakges")
    config.set(
        "logic pacakges", "; Uncomment following exmaple and replace with your cohesive packages in each module. ")

    for m, packages in logic_pacakges.items():
        config.set("logic pacakges", m, json.dumps(packages, indent=2))


def read_bad_smells(config: configparser.ConfigParser) -> list[BadSmell]:
    """
    >>> sample_config = '''
    ... [bad smells]
    ...   BadSmellCrossModule
    ...   BadSmellCrossPackage
    ...   BadSmellCylicDependency
    ...   ShouldNotDepend: [
    ...       {
    ...         "from": {"module": "app", "package": "com.prettifier.pretty.helper" },
    ...        "to": {"module": "app", "package": "com.fastaccess.data.dao", "name": "NameParser"}
    ...       }
    ...     ]
    ... '''
    >>> config = configparser.ConfigParser(allow_no_value=True)
    >>> config.optionxform = str
    >>> config.read_string(sample_config)
    >>> bad_smells = read_bad_smells(config)
    >>> print([type(s).__name__ for s in bad_smells])
    ['BadSmellCrossModule', 'BadSmellCrossPackage', 'BadSmellCylicDependency', 'ShouldNotDepend']
    """
    module = __import__("smells")
    bad_smells = []
    if config.has_section('bad smells'):
        for smell_name, params_json in config.items('bad smells'):
            if params_json:
                smell_class_ = getattr(module, smell_name)
                for params in json.loads(params_json):
                    if smell_name == "ShouldNotDepend":
                        bad_smells.append(
                            smell_class_(params["from"], params["to"]))
                    else:
                        bad_smells.append(
                            smell_class_(**params))
            else:
                smell_class_ = getattr(module, smell_name)
                bad_smells.append(smell_class_())
    return bad_smells


def write_bad_smells(config: configparser.ConfigParser, bad_smells: list[BadSmell] = example_bad_smells):
    def sorter(bs): return type(bs).__name__
    config.add_section("bad smells")
    config.set(
        "bad smells", "; Uncomment following smells and replace with your rules ")
    for t, bs_list in groupby(sorted(bad_smells, key=sorter), key=sorter):
        args_list = [bs.all_args for bs in bs_list if bs.all_args]
        config.set("bad smells", t, json.dumps(
            args_list, indent=2) if len(args_list) > 0 else None)


def read_layers(config: configparser.ConfigParser) -> dict[str: list[dict[str:str]]]:
    """
    >>> sample_config = '''
    ... [layers]
    ...   platform = [
    ...       { "module": "app", "package": "com.prettifier.pretty.helper" }
    ...     ]
    ... '''
    >>> config = configparser.ConfigParser(allow_no_value=True)
    >>> config.optionxform = str
    >>> config.read_string(sample_config)
    >>> layers = read_layers(config)
    >>> print(layers)
    {'platform': [{'module': 'app', 'package': 'com.prettifier.pretty.helper'}]}
    """
    layers = {}
    if config.has_section('layers'):
        for layer_name, _json in config.items('layers'):
            layers[layer_name] = json.loads(_json)
    return layers


def write_layers(config: configparser.ConfigParser, layers: dict[str: list[dict[str:str]]] = exmaple_layers):
    config.add_section("layers")
    config.set("layers", "; Desired layers")
    for k, v in layers.items():
        config.set("layers", k, json.dumps(v, indent=2))


def write_example_config(config: configparser.ConfigParser, file_path: str):
    write_logic_packages(config)
    write_layers(config)
    write_bad_smells(config)

    lines = ""
    with io.StringIO() as ss:
        config.write(ss)
        ss.seek(0)
        lines = "".join([('; ' if not l.startswith(
            "[") else '') + l for l in ss.readlines()])

    with open(file_path, 'w', encoding="utf-8") as configfile:
        configfile.writelines(lines)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
