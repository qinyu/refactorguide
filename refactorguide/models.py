# coding=utf-8

import fnmatch
from itertools import groupby
from operator import attrgetter
from typing import Dict, List
from abc import ABCMeta, abstractmethod

sorter = attrgetter('module', 'package', 'name')


class Component(metaclass=ABCMeta):

    @property
    @abstractmethod
    def dependencies(self):
        pass

    @property
    @abstractmethod
    def usages(self):
        pass

    @property
    def smell_dependencies(self):
        return [d for d in self.dependencies if d.has_smell]

    @property
    def smell_usages(self):
        return [u for u in self.usages if u.has_smell]


class ComponentList(Component, metaclass=ABCMeta):

    @property
    def dependencies(self):
        return sorted(set([d for c in self.classes for d in c.dependencies]), key=sorter)

    @property
    def usages(self):
        return sorted(set([u for c in self.classes for u in c.usages]), key=sorter)

    def __init__(self, name, parent=None) -> None:
        super().__init__()
        self.name = name
        self.parent = parent

    @property
    def items(self) -> List[Component]:
        return self._items

    @items.setter
    def items(self, items: List[Component]):
        self._items = sorted(items, key=attrgetter("name"))

    def __getitem__(self, key: str) -> Component:
        return next((p for p in self._items if p.name == key), None)

    def __setitem__(self, key: str, component: Component):
        finded = self.__getitem__(key)
        if not finded:
            self._items.append(component)
            self._items = sorted(self._items, key=attrgetter("name"))

    @property
    def classes(self):
        return [c for p in self.items for c in p.classes]


class ClassInfo(object):
    def __init__(self, path, full_name, package, module, layer, category):
        self.layer = layer
        self.category = category
        self.path = path
        self.full_name = full_name
        self.package = package
        self.module = module

    @property
    def name(self):
        return self.full_name[len(self.package)+1:]

    @property
    def is_production(self):
        return self.category == "Production"

    def is_layer(self, layer):
        return self.layer == layer

    def oneline_str(self, template):
        return template.format(**self.all_attributes)

    @property
    def all_attributes(self):
        all_attrs = dict(vars(self), name=self.name)
        all_attrs['class'] = all_attrs['name']
        return all_attrs

    def wildcards_macth(self, **kwargs):
        for attr_name, wildcards in kwargs.items():
            if not fnmatch.fnmatch(self.all_attributes.get(attr_name), wildcards):
                return False
        return True

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, ClassInfo):
            return self.path == other.path
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.path)


class Class(ClassInfo, Component):

    def __init__(self, path, full_name, package, module, layer=None, category="Production", dependencies=[]):
        self.dependencies = dependencies
        self.usages = []
        super().__init__(path, full_name, package, module, layer, category)

    @property
    def dependencies(self):
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies):
        self._dependencies = sorted(dependencies, key=sorter)

    @property
    def usages(self):
        return self._usages

    @usages.setter
    def usages(self, usages):
        self._usages = sorted(usages, key=sorter)


class Dependency(ClassInfo):
    def __init__(self, path, full_name, package, module, layer, category):
        super().__init__(path, full_name, package, module, layer, category)
        self.bad_smells = []

    def __eq__(self, other):
        if isinstance(other, Dependency):
            return super().__eq__(other)
        return False

    @property
    def has_smell(self):
        return len(self.bad_smells) > 0

    def oneline_str(self, template):
        _str = super().oneline_str(template)
        if self.has_smell:
            _str += " (" + "; ".join(
                [bs.description for bs in self.bad_smells]) + ")  "
        return _str

    def __hash__(self):
        return hash(self.path)


class Package(ComponentList):

    def __init__(self, name, module, classes, layer=None):
        self.classes = classes
        super().__init__(name, parent=module)
        self.layer = layer

    @property
    def module(self):
        return self.parent

    @property
    def package(self):
        return self.name

    @property
    def classes(self) -> List[Class]:
        return self._classes

    @classes.setter
    def classes(self, classes):
        self._classes = sorted(classes, key=sorter)

    @property
    def items(self):
        return self._classes

    @items.setter
    def items(self, items):
        self._classes = items

    def __getitem__(self, key: str) -> Class:
        return next((c for c in self._classes if c.full_name[len(self.package)+1:] == key), None)

    def oneline_str(self, template):
        return template.format(**self.all_attributes)

    @property
    def all_attributes(self):
        return dict(vars(self), full_name=self.name, module=self.module)


class Module(ComponentList):

    def __init__(self, name: str, layer: str, packages: List[Package]):
        self.packages = packages
        super().__init__(name, parent=layer)

    @property
    def module(self):
        return self.name

    @property
    def layer(self):
        return self.parent

    @property
    def packages(self) -> List[Package]:
        return self.items

    @packages.setter
    def packages(self, packages: List[Package]):
        self.items = packages


class Layer(ComponentList):

    def __init__(self, name: str, modules: List[Module]):
        self.modules = modules
        super().__init__(name)

    @property
    def modules(self) -> List[Module]:
        return self.items

    @modules.setter
    def modules(self, modules: List[Module]):
        self.items = modules

    @property
    def layer(self):
        return self.name


class Hierarchy(ComponentList):

    def __init__(self, layers):
        super().__init__('Hierarchy')
        self.items = layers

    @property
    def layers(self) -> List[Layer]:
        return self.items

    @layers.setter
    def layers(self, layers: List[Layer]):
        self.items = layers


def group_class_by_module_package(classes: List[Class]) -> Dict[str, Dict[str, Class]]:
    """Group class by its attributes: 'module', 'pacakge' and 'name', returns an embeded dict"""
    module_dict = {}
    sorted_classes = sorted(classes, key=sorter)
    for m, m_cls_list in groupby(sorted_classes, key=attrgetter("module")):
        package_dict = {}
        for p, p_cls_list in groupby(list(m_cls_list), key=attrgetter("package")):
            package_dict[p] = list(p_cls_list)

        module_dict[m] = package_dict
    return module_dict
