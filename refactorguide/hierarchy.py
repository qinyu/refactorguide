from refactorguide.desgin import LAYER_UNKNOWN
from typing import Dict, List
from refactorguide.models import Class, Component, ComponentList, Dependency, Hierarchy, Layer, Module, Package, \
    group_class_by_module_package, path_to_wd_dict


def _build_module(layer_name: str,
                  module_name: str,
                  grouped_classes: Dict[str, List[Class]]):
    module = Module(module_name, list(), layer_name)
    for package_name, classes in grouped_classes.items():
        package = module[package_name]
        if package:
            package.classes = package.classes + classes  # sort
        else:
            module[package_name] = Package(
                package_name, classes, module.name)
    return module


def _seperate_layer(old_layer: Layer,
                    new_layer_name,
                    **wildcards_dict):
    match_modules, unmatch_modules = old_layer.separate_items(
        wildcards_dict.get('module', None))

    final_match_modules, final_unmatch_modules = _recursive_seperate_items(
        wildcards_dict.get('package', None),
        wildcards_dict.get('class', None),
        match_modules,
        unmatch_modules,
        Module,
        new_layer_name)

    return Layer(new_layer_name, final_match_modules), Layer(old_layer.name, final_unmatch_modules)


def _recursive_seperate_items(wildcards,
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
            final_match_child_items, final_unmatch_child_items = match_item.separate_items(
                wildcards)

            final_match_child_items, final_unmatch_child_items = _recursive_seperate_items(
                child_wildcards,
                None,
                final_match_child_items,
                final_unmatch_child_items,
                Package)

            if final_match_child_items:
                component_list_parent = new_parent if new_parent else match_item.parent
                final_match_items.append(
                    component_list_type(match_item.name,
                                        final_match_child_items, component_list_parent))
            if final_unmatch_child_items:
                final_unmatch_items.append(
                    component_list_type(match_item.name,
                                        final_unmatch_child_items, match_item.parent))
    return final_match_items, final_unmatch_items


def _fill_layer_name_and_usages(classes, layers):
    _fill_classes_layer_name(layers)

    class_map = dict((c.path, c) for c in classes)
    for layer in layers:
        layer_name = layer.name
        for cls in layer.classes:
            cls.layer = layer_name
            for d in cls.dependencies:
                c = class_map.get(d.path)
                if not c:
                    # print("can't find dep:" + d.path)
                    continue

                d.layer = c.layer
                # if not d.layer:
                #     print("can't find dep layer:" + d.path)
                usage = Dependency(cls.path, cls.name, cls.package, cls.module, cls.layer)
                c.usages = [*c.usages, usage]


def _fill_classes_layer_name(layers):
    for layer in layers:
        layer_name = layer.name
        for module in layer.modules:
            for package in module.packages:
                package.layer = layer_name
                for cls in package.classes:
                    cls.layer = layer_name


def _seperate_layers(layer_designs, unknown_layer):
    layers = []
    unmatch_layer = unknown_layer
    for layer_name, wildcards_dict_list in layer_designs.items():
        new_layer = Layer(layer_name, [])
        for wildcards_dict in sorted([path_to_wd_dict(wd) for wd in wildcards_dict_list], key=len, reverse=True):
            if missing_wildcards(wildcards_dict):
                continue

            match_layer, unmatch_layer = _seperate_layer(unmatch_layer,
                                                         layer_name,
                                                         **wildcards_dict)
            new_layer.items = new_layer.items + match_layer.items
        layers.append(new_layer)
    layers.append(unmatch_layer)
    return layers


def _build_unknown_layer(classes):
    module_dict = group_class_by_module_package(classes)
    unknown_layer = Layer(LAYER_UNKNOWN, [])
    unknown_layer.modules = [_build_module(unknown_layer.name,
                                           module_name,
                                           package_dict)
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


def _add_to(component: Component, container: ComponentList):
    item_type_name = container.item_type.__name__.lower()
    item_key = component.hierarchy_path.get(item_type_name, None)
    if item_key:
        if container.item_type == type(component):
            container[item_key] = component
        else:
            container[item_key] = container.item_type(
                item_key, list(), **component.hierarchy_path)
            _add_to(component, container[item_key])

    return container


def _remove_from(component: Component, container: ComponentList):
    item_type_name = container.item_type.__name__.lower()
    item_key = component.hierarchy_path.get(item_type_name, None)
    if item_key:
        if container.item_type == type(component):
            del container[item_key]
        else:
            item = container[item_key]
            if item:
                _remove_from(component, item)
                if not item.items:
                    del container[item_key]
    return container


def filter_hierarchy(container: ComponentList,
                     path_patterns: Dict[str, str] or str,
                     hierarchy: Hierarchy) -> Hierarchy:
    path_wildcards = path_to_wd_dict(path_patterns)
    item_type_name = container.item_type.__name__.lower()
    item_path_pattern = path_wildcards.get(item_type_name, None)
    items = container.find_items(item_path_pattern)

    if issubclass(container.item_type, ComponentList):
        for item in items:
            filter_hierarchy(item, path_wildcards, hierarchy)
    else:
        for item in items:
            _add_to(item, hierarchy)

    return hierarchy


def build_hierarchy(classes: List[Class],
                    layer_designs: Dict[str, List[Dict[str, str]]]):
    unknown_layer = _build_unknown_layer(classes)
    layers = _seperate_layers(layer_designs, unknown_layer)
    _fill_layer_name_and_usages(classes, layers)

    return Hierarchy(layers)
