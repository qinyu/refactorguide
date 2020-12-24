# coding = utf-8s
from configparser import ConfigParser as CP
import io
import json
import importlib
import configparser
import os
from refactorguide.smells import Smell, SmellDependency, SmellDependencyCrossModule, \
    SmellDependencyCrossPackage, SmellCylicDependency
from itertools import groupby

from typing import List, Dict

from refactorguide.desgin import set_smells, set_layers, set_logic_packages

LAYERS_SECTION = "layers"
LOGIC_PACKAGES_SECTION = "logic packages"
SMELLS_SECTION = "bad smells"

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

example_smells = [
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
    logic_pacakges = {}
    if cp.has_section(LOGIC_PACKAGES_SECTION):
        for m, packages_json in cp.items(LOGIC_PACKAGES_SECTION):
            if packages_json:
                logic_pacakges[m] = json.loads(packages_json)
            else:
                print("Warning: no packages specified in {}".format(m))
    return logic_pacakges


def write_logic_packages(cp: CP, logic_pacakges: Dict[str, List[str]]):
    cp.add_section(LOGIC_PACKAGES_SECTION)
    cp.set(LOGIC_PACKAGES_SECTION,
           "; Uncomment following exmaple and replace with your cohesive packages in each module. ")

    for module, packages in logic_pacakges.items():
        cp.set(LOGIC_PACKAGES_SECTION, module, json.dumps(packages, indent=2))


def read_smells(cp: CP) -> List[Smell]:
    module = importlib.import_module("refactorguide.smells")
    bad_smells = []
    if cp.has_section(SMELLS_SECTION):
        for smell_name, params_json in cp.items(SMELLS_SECTION):
            if params_json:
                smell_class_ = getattr(module, smell_name)
                for params in json.loads(params_json):
                    bad_smells.append(smell_class_(**params))
            else:
                smell_class_ = getattr(module, smell_name)
                bad_smells.append(smell_class_())
    return bad_smells


def write_smells(cp: CP, bad_smells: List[Smell]):
    def sorter(bs): return type(bs).__name__
    cp.add_section(SMELLS_SECTION)
    cp.set(SMELLS_SECTION, "; Uncomment following smells and replace with your rules ")
    for t, bs_list in groupby(sorted(bad_smells, key=sorter), key=sorter):
        args_list = [bs.all_args for bs in bs_list if bs.all_args]
        cp.set(SMELLS_SECTION, t, json.dumps(
            args_list, indent=2) if len(args_list) > 0 else None)


def read_layers(cp: CP) -> Dict[str, List[Dict[str, str]]]:
    layers = {}
    if cp.has_section(LAYERS_SECTION):
        for layer_name, _json in cp.items(LAYERS_SECTION):
            layers[layer_name] = json.loads(_json)
    return layers


def write_layers(cp: CP, layers: Dict[str, List[Dict[str, str]]]):
    cp.add_section(LAYERS_SECTION)
    cp.set(LAYERS_SECTION, "; Desired layers")
    for k, v in layers.items():
        cp.set("layers", k, json.dumps(v, indent=2))


def write_design_file(cp: CP, file_path: str, logic_pacakges, layers, smells):
    write_logic_packages(cp, logic_pacakges)
    write_layers(cp, layers)
    write_smells(cp, smells)

    lines = ""
    with io.StringIO() as ss:
        cp.write(ss)
        ss.seek(0)
        lines = "".join([('; ' if not line.startswith(
            "[") else '') + line for line in ss.readlines()])

    with open(file_path, 'w', encoding="utf-8") as designfile:
        designfile.writelines(lines)


def load_design_file(design_file_path, generate_example=False):
    cp = configparser.ConfigParser(allow_no_value=True)
    cp.optionxform = str

    if os.path.exists(design_file_path):
        with open(design_file_path, 'r') as design_file:
            cp.read_string(design_file.read())
        set_logic_packages(read_logic_pacakges(cp))
        set_layers(read_layers(cp))
        set_smells(read_smells(cp))
    elif generate_example:
        write_design_file(
            cp, design_file_path, example_logic_pacakges, exmaple_layers, example_smells)
