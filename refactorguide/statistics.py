import itertools
import operator
from refactorguide.smells import Smell
from typing import Dict, List, Tuple
from refactorguide.models import Class, Component, ComponentList, Dependency, Hierarchy


def console_statistics_data(hierarchy: Hierarchy):
    total_smell = {}
    total_module = 0
    total_package = 0
    total_class = 0
    total_dependencies = 0
    total_usages = 0

    total_smell_dependencies = 0
    total_smell_usages = 0

    all_package_list = []
    all_classes_list = []

    for layer in hierarchy.layers:
        for module in layer.modules:
            total_module += 1
            for pkg in module.packages:
                if(pkg not in all_package_list):
                    all_package_list.append(pkg)
                total_package += 1
                total_class += len(pkg.classes)
                total_dependencies += len(pkg.dependencies)
                total_usages += len(pkg.usages)
                total_smell_dependencies += len(pkg.smell_dependencies)
                total_smell_usages += len(pkg.smell_usages)
                for file in pkg.classes:
                    if(file not in all_classes_list):
                        all_classes_list.append(file)
                    for d in file.dependencies:
                        for s in d.bad_smells:
                            if(s not in total_smell.keys()):
                                total_smell.setdefault(s)
                                total_smell[s] = 1
                            else:
                                total_smell[s] += 1
    # 输出整体统计数据
    print(statistics_format.format(total_module, total_package, total_class,
                                   total_dependencies, total_usages, total_smell_dependencies, total_smell_usages))
    # 输出rule统计数据
    sort_list = sorted(total_smell.items(),
                       key=lambda kv: (kv[1], kv[0]), reverse=True)
    for sort_dict in sort_list:
        print(rule_format.format(sort_dict[0].description, str(sort_dict[1])))
    print_top_package(all_package_list)
    print_top_classes(all_classes_list)


def print_top_package(all_package_list):
    # 输出Top问题包
    sort_dep_list = sorted(all_package_list, key=lambda pkg: len(
        pkg.smell_dependencies), reverse=True)

    print("\n"+"依赖数量Top 10 包:")
    for i in range(0, 10):
        pkg = sort_dep_list[i]
        print(p_format.format(pkg.name, pkg.module,
                              len(pkg.smell_dependencies)))

    sort_usages_list = sorted(all_package_list, key=lambda pkg: len(
        pkg.smell_usages), reverse=True)

    print("\n"+"被引用数量Top 10 包:")
    for i in range(0, 10):
        pkg = sort_usages_list[i]
        print(p_format.format(pkg.name, pkg.module, len(pkg.smell_usages)))


def print_top_classes(all_classes_list):
    # 输出Top问题类
    sort_dep_classes_list = sorted(all_classes_list, key=lambda file: len(
        file.smell_dependencies), reverse=True)

    print("\n"+"依赖数量Top 10 类:")
    for i in range(0, 10):
        file = sort_dep_classes_list[i]
        print(c_format.format(file.name, file.package,
                              file.module, len(file.smell_dependencies)))

    sort_usages_classes_list = sorted(
        all_classes_list, key=lambda file: len(file.smell_usages), reverse=True)

    print("\n"+"被引用数量Top 10 类:")
    for i in range(0, 10):
        file = sort_usages_classes_list[i]
        print(c_format.format(file.name, file.package,
                              file.module, len(file.smell_usages)))


statistics_format = '''
Statistics:

模块：{}  包：{}  类文件：{}
依赖数量：{}   引用数量：{}
可疑依赖数量：{}   可疑引用数量：{}
'''
rule_format = '''BasSmell-{}：{} '''

p_format = '''包：{} 模块：{} 数量：{}'''

c_format = '''类：{} 包：{} 模块：{} 数量：{}'''


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
    sdc_list = [(s, d, c) for c in classes for d in c.dependencies for s in d.bad_smells]
    for smell, s_sdc_list in itertools.groupby(sdc_list, operator.itemgetter(0)):
        dependency_group = {}
        for dependency, d_sdc_list in itertools.groupby(list(s_sdc_list), operator.itemgetter(1)):
            dependency_group[dependency] = list(d_sdc_list)
        smell_group[smell] = dependency_group
    return smell_group


smells_statistics_headers = ["坏味道", "影响的依赖数(*)"]


def smells_statistics(smell_group: Dict[Smell, Dict[Dependency, List[Tuple[Smell, Dependency, Class]]]]):
    def _smell_data(smell: Smell, dependency_group: Dict[Dependency, List[Tuple[Smell, Dependency, Class]]]):
        return [
            type(smell).__name__,
            len(dependency_group.items()),
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
