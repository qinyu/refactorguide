import fnmatch
from refactorguide.desgin import LAYER_UNKNOWN
from typing import Dict, List
from refactorguide.models import Class, ComponentList, Dependency, Hierarchy, Layer, Module, Package, \
    group_class_by_module_package


def __build_module(layer_name: str,
                   module_name: str,
                   grouped_classes: Dict[str, List[Class]],
                   desired_packages: List[str]):
    module = Module(module_name, layer_name,  [])
    for package_name, classes in grouped_classes.items():
        desired_package_name = next((p for p in desired_packages if package_name.startswith(p)),
                                    package_name)
        package = module[desired_package_name]
        if package:
            package.classes = package.classes + classes  # sort
        else:
            module[desired_package_name] = Package(
                desired_package_name, module.name, classes)
    return module


def __seperate_items(component_list: ComponentList, match_wildcards):
    match_items, unmatch_items = [], []
    for item in component_list.items:
        match_items.append(item) if not match_wildcards or fnmatch.fnmatch(
            item.name, match_wildcards) else unmatch_items.append(item)
    return match_items, unmatch_items


def __seperate_layer(layer: Layer,
                     new_layer_name,
                     **wildcards_dict):
    match_modules, unmatch_modules = __seperate_items(
        layer, wildcards_dict.get('module', None))

    final_match_modules, final_unmatch_modules = __recursive_seperate_items(
        wildcards_dict.get('package', None),
        wildcards_dict.get('class', None),
        match_modules,
        unmatch_modules,
        Module,
        new_layer_name)

    return Layer(new_layer_name, final_match_modules), Layer(layer.name, final_unmatch_modules)


def __recursive_seperate_items(wildcards,
                               child_wildcards,
                               match_items,
                               unmatch_items,
                               component_list_type,
                               new_parent=None):
    final_match_items = list(match_items)
    final_unmatch_items = list(unmatch_items)
    if wildcards:
        final_match_items = []
        for match_item in match_items:
            final_match_child_items, final_unmatch_child_items = __seperate_items(
                match_item, wildcards)

            final_match_child_items, final_unmatch_child_items = __recursive_seperate_items(
                child_wildcards,
                None,
                final_match_child_items,
                final_unmatch_child_items,
                Package)

            if final_match_child_items:
                component_list_parent = new_parent if new_parent else match_item.parent
                final_match_items.append(
                    component_list_type(match_item.name, component_list_parent, final_match_child_items))
            if final_unmatch_child_items:
                final_unmatch_items.append(
                    component_list_type(match_item.name, match_item.parent, final_unmatch_child_items))
    return final_match_items, final_unmatch_items


def __fill_layer_name_and_usages(classes, layers):
    class_map = dict((c.path, c) for c in classes)
    for layer in layers:
        layer_name = layer.name
        for module in layer.modules:
            for package in module.packages:
                package.layer = layer_name

        for cls in layer.classes:
            cls.layer = layer_name
            for d in cls.dependencies:
                c = class_map.get(d.path)
                if not c:
                    continue

                d.layer = c.layer
                usage = Dependency(cls.path, cls.full_name,
                                   cls.package, cls.module,  cls.layer, cls.category)
                c.usages = [*c.usages, usage]


def __seperate_layers(layer_designs, unknown_layer):
    layers = []
    unmatch_layer = unknown_layer
    for layer_name, wildcards_dict_list in layer_designs.items():
        new_layer = Layer(layer_name, [])
        for wildcards_dict in sorted(wildcards_dict_list, key=len, reverse=True):
            if missing_wildcards(wildcards_dict):
                continue

            match_layer, unmatch_layer = __seperate_layer(unmatch_layer,
                                                          layer_name,
                                                          **wildcards_dict)
            new_layer.items = new_layer.items + match_layer.items
        layers.append(new_layer)
    layers.append(unmatch_layer)
    return layers


def __build_unknown_layer(classes, package_design):
    module_dict = group_class_by_module_package(classes)
    unknown_layer = Layer(LAYER_UNKNOWN, [])
    unknown_layer.modules = [__build_module(unknown_layer.name,
                                            module_name,
                                            package_dict,
                                            package_design.get(module_name, []))
                             for module_name, package_dict in module_dict.items()]
    return unknown_layer


def missing_wildcards(wildcards_dict):
    if 'class' in wildcards_dict.keys() and 'package' not in wildcards_dict.keys():
        print("Warning: missing package {}".format(wildcards_dict))
        return True

    if 'module' not in wildcards_dict.keys():
        print("Warning: missing module {}".format(wildcards_dict))
        return True

    return False


def build_hierachy(classes: List[Class],
                   layer_designs: Dict[str, List[Dict[str, str]]],
                   package_design: Dict[str, List[str]]):

    unknown_layer = __build_unknown_layer(classes, package_design)
    layers = __seperate_layers(layer_designs, unknown_layer)
    __fill_layer_name_and_usages(classes, layers)

    return Hierarchy(layers)
