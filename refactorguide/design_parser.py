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

from refactorguide.desgin import Design

LAYERS_SECTION = "layers"
SMELLS_SECTION = "smells"

exmaple_layers = {
    "application": [],
    "business": [
        {"module": "In_this_module",
         "package": "in.this.packqge",
         "name": "OnlyThisClassBelongsToBusinessLayer"}
    ],
    "service":  [
        {"module": "Whole_module_belongs_to_service_layer"}
    ],
    "platform":  [
        {"path": ":In_this_module:only.this.package.belongs.to.platform.layer"}
    ]
}

example_smells = [
    SmellDependency(**{
        'from': ':OneModule',
        'to': 'AnotherModule'
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


def _read_smells(cp: CP) -> List[Smell]:
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


def _write_smells(cp: CP, bad_smells: List[Smell]):
    def sorter(bs): return type(bs).__name__
    if not cp.has_section(SMELLS_SECTION):
        cp.add_section(SMELLS_SECTION)
        cp.set(SMELLS_SECTION,
               "; Uncomment following smells and replace with your rules ")
    for t, bs_list in groupby(sorted(bad_smells, key=sorter), key=sorter):
        args_list = [bs.all_args for bs in bs_list if bs.all_args]
        cp.set(SMELLS_SECTION, t, json.dumps(
            args_list, indent=2) if len(args_list) > 0 else None)


def _read_layers(cp: CP) -> Dict[str, List[Dict[str, str]]]:
    layers = {}
    if cp.has_section(LAYERS_SECTION):
        for layer_name, _json in cp.items(LAYERS_SECTION):
            layers[layer_name] = json.loads(_json)
    return layers


def _write_layers(cp: CP, layers: Dict[str, List[Dict[str, str]]]):
    if not cp.has_section(LAYERS_SECTION):
        cp.add_section(LAYERS_SECTION)
        cp.set(LAYERS_SECTION, "; Desired layers")
    for k, v in layers.items():
        cp.set(LAYERS_SECTION, k, json.dumps(v, indent=2))


def _write_design(cp, file_path):
    lines = ""
    with io.StringIO() as ss:
        cp.write(ss)
        ss.seek(0)
        lines = "".join([('; ' if not line.startswith(
            "[") else '') + line for line in ss.readlines()])
    with open(file_path, 'w', encoding="utf-8") as designfile:
        designfile.writelines(lines)


def load_design(design_file_path, generate_example=False):
    default_design = Design({}, [SmellDependencyCrossModule(),
                                 SmellDependencyCrossPackage(),
                                 SmellCylicDependency()])
    cp = configparser.ConfigParser(allow_no_value=True)
    cp.optionxform = str

    if os.path.exists(design_file_path):
        with open(design_file_path, 'r', encoding='utf-8') as design_file:
            cp.read_string(design_file.read())
        return Design(_read_layers(cp), _read_smells(cp))
    elif generate_example:
        _write_layers(cp, default_design.layers)
        _write_layers(cp, exmaple_layers)

        _write_smells(cp, default_design.smells)
        _write_smells(cp, example_smells)

        _write_design(cp, design_file_path)

    return default_design
