import fnmatch
from refactorguide.desgin import LAYER_UNKNOWN
from typing import Dict, List
from refactorguide.models import Class, Container, Dependency, Hierarchy, Layer, Module, Package, \
    group_class_by_module_package


def build_module(layer_name: str,
                 module_name: str,
                 classes_grouped_by_package: Dict[str, List[Class]],
                 desired_packages: List[str]):
    module = Module(module_name, layer_name,  [])
    for package_name, classes in classes_grouped_by_package.items():
        desired_package_name = next((p for p in desired_packages if package_name.startswith(p)),
                                    package_name)
        package = module[desired_package_name]
        if not package:
            module[desired_package_name] = Package(
                desired_package_name, module.name, classes)
        else:
            package.classes = package.classes + classes  # sort
    return module


def divide_children(container: Container, wildcards):
    match_children, unmatch_children = [], []
    for child in container.children:
        match_children.append(child) if not wildcards or fnmatch.fnmatch(
            child.name, wildcards) else unmatch_children.append(child)
    return match_children, unmatch_children


def divide_layer(layer: Layer,
                 new_layer_name,
                 **wildcards_dict):
    match_modules, unmatch_modules = divide_children(
        layer, wildcards_dict.get('module', None))

    final_match_modules, final_unmatch_modules = recursive_match(
        wildcards_dict.get('package', None),
        wildcards_dict.get('class', None),
        match_modules,
        unmatch_modules,
        Module,
        new_layer_name)

    return Layer(new_layer_name, final_match_modules), Layer(layer.name, final_unmatch_modules)


def recursive_match(child_wildcards,
                    grandchild_wildcards,
                    match_containers,
                    unmatch_conntainers,
                    container_type,
                    new_parent=None):
    final_match_containers = list(match_containers)
    final_unmatch_containers = list(unmatch_conntainers)
    if child_wildcards:
        final_match_containers = []
        for match_container in match_containers:
            final_match_children, final_unmatch_children = divide_children(
                match_container, child_wildcards)

            final_match_children, final_unmatch_children = recursive_match(
                grandchild_wildcards,
                None,
                final_match_children,
                final_unmatch_children,
                Package)

            if final_match_children:
                container_parent = new_parent if new_parent else match_container.parent
                final_match_containers.append(
                    container_type(match_container.name, container_parent, final_match_children))
            if final_unmatch_children:
                final_unmatch_containers.append(
                    container_type(match_container.name, match_container.parent, final_unmatch_children))
    return final_match_containers, final_unmatch_containers


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

    module_dict = group_class_by_module_package(classes)
    unknown_layer = Layer(LAYER_UNKNOWN, [])
    unknown_layer.modules = [build_module(unknown_layer.name,
                                          module_name,
                                          package_dict,
                                          package_design.get(module_name, []))
                             for module_name, package_dict in module_dict.items()]

    layers = []
    for layer_name, wildcards_dict_list in layer_designs.items():
        new_layer = Layer(layer_name, [])
        for wildcards_dict in sorted(wildcards_dict_list, key=lambda d: len(d), reverse=True):
            if missing_wildcards(wildcards_dict):
                continue
            match_layer, unknown_layer = divide_layer(unknown_layer,
                                                      layer_name,
                                                      **wildcards_dict)
            new_layer.children = new_layer.children + match_layer.children
        layers.append(new_layer)
    layers.append(unknown_layer)

    class_map = dict((c.path, c) for c in classes)
    for layer in layers:
        layer_name = layer.name
        for module in layer.modules:
            for package in module.packages:
                package.layer = layer_name
                for cls in package.classes:
                    cls.layer = layer_name

                    for d in cls.dependencies:
                        c = class_map.get(d.path)
                        if c:
                            d.layer = c.layer
                            usage = Dependency(cls.path, cls.full_name,
                                               cls.package, cls.module,  cls.layer, cls.category)
                            c.usages = [*c.usages, usage]

    return Hierarchy(layers)
