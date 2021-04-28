import itertools
import operator
from refactorguide.smells import Smell
from typing import Dict, List, Tuple
from refactorguide.models import Class, Component, ComponentList, Dependency


components_statistics_headers = ["名称", "依赖数", "坏味道依赖数(*)", "类个数", "坏味道类个数"]


def components_statistics(components: List[Component]):
    def _component_data(component: Component):
        return [
            component.name,
            len(component.dependencies),
            len(component.smell_dependencies),
            len(component.classes) if isinstance(component, ComponentList) else "N/A",
            len(component.smell_dependency_classes) if isinstance(component, ComponentList) else "N/A"
        ]
    return sorted([_component_data(c) for c in components], key=operator.itemgetter(2), reverse=True)


def group_classes_by_smell_dependency(classes: List[Class]) \
        -> Dict[Smell, Dict[Dependency, List[Tuple[Smell, Dependency, Class]]]]:
    smell_group = {}
    sdc_sorted_by_s = sorted([(s, d, c) for c in classes for d in c.dependencies for s in d.bad_smells],
                             key=lambda sdc: str(sdc[0]))
    for smell, s_sdc_list in itertools.groupby(sdc_sorted_by_s, operator.itemgetter(0)):
        sdc_sorted_by_d = sorted(list(s_sdc_list), key=lambda sdc: sdc[1].path)

        dependency_group = {}
        for dependency, d_sdc_list in itertools.groupby(sdc_sorted_by_d, operator.itemgetter(1)):
            sdc_sorted_by_c = sorted(list(d_sdc_list), key=lambda sdc: sdc[2].path)
            dependency_group[dependency] = sdc_sorted_by_c

        smell_group[smell] = dependency_group

    return smell_group


smells_statistics_headers = ["坏味道", "影响的依赖数 (*)", "影响的类个数 (*)"]


def smells_statistics(smell_group: Dict[Smell, Dict[Dependency, List[Tuple[Smell, Dependency, Class]]]]):
    def _smell_data(smell: Smell, dependency_group: Dict[Dependency, List[Tuple[Smell, Dependency, Class]]]):
        return [
            smell,
            len(dependency_group.items()),
            sum([len(v) for v in dependency_group.values()])
        ]

    statistics_data = [_smell_data(s, dependency_group) for s, dependency_group in smell_group.items()]
    return sorted(statistics_data, key=operator.itemgetter(1), reverse=True)


dependencies_statistics_headers = ["依赖", "影响的类个数(*)"]


def dependencies_statistics(dependency_group: Dict[Dependency, List[Tuple[Smell, Dependency, Class]]]):
    def _dependency_data(dependency: Dependency, sdc_list: List[Tuple[Smell, Dependency, Class]]):
        return [
            dependency.full_name,
            len(sdc_list),
        ]
    statistics_data = [_dependency_data(d, sdc_list) for d, sdc_list in dependency_group.items()]
    return sorted(statistics_data, key=operator.itemgetter(1), reverse=True)
