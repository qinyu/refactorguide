def console_statistics_data(module_dict):
    total_smell = {}
    total_module = 0
    total_package = 0
    total_class = 0
    total_dependencies = 0
    total_usages = 0

    total_suspicious_dependencies = 0
    total_suspicious_usages = 0

    all_package_list = []
    all_classes_list = []

    for m, pkg_dict in module_dict.items():
        total_module += 1
        for p, pkg in pkg_dict.items():
            if(pkg not in all_package_list):
                all_package_list.append(pkg)
            total_package += 1
            total_class += len(pkg.classes)
            total_dependencies += len(pkg.dependencies)
            total_usages += len(pkg.usages)
            total_suspicious_dependencies += len(pkg.suspicious_dependencies)
            total_suspicious_usages += len(pkg.suspicious_usages)
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
                                   total_dependencies, total_usages, total_suspicious_dependencies, total_suspicious_usages))
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
        pkg.suspicious_dependencies), reverse=True)

    print("\n"+"依赖数量Top 10 包:")
    for i in range(0, 10):
        pkg = sort_dep_list[i]
        print(p_format.format(pkg.name, pkg.module,
                              len(pkg.suspicious_dependencies)))

    sort_usages_list = sorted(all_package_list, key=lambda pkg: len(
        pkg.suspicious_usages), reverse=True)

    print("\n"+"被引用数量Top 10 包:")
    for i in range(0, 10):
        pkg = sort_usages_list[i]
        print(p_format.format(pkg.name, pkg.module, len(pkg.suspicious_usages)))


def print_top_classes(all_classes_list):
    # 输出Top问题类
    sort_dep_classes_list = sorted(all_classes_list, key=lambda file: len(
        file.suspicious_dependencies), reverse=True)

    print("\n"+"依赖数量Top 10 类:")
    for i in range(0, 10):
        file = sort_dep_classes_list[i]
        print(c_format.format(file.name, file.package,
                              file.module, len(file.suspicious_dependencies)))

    sort_usages_classes_list = sorted(
        all_classes_list, key=lambda file: len(file.suspicious_usages), reverse=True)

    print("\n"+"被引用数量Top 10 类:")
    for i in range(0, 10):
        file = sort_usages_classes_list[i]
        print(c_format.format(file.name, file.package,
                              file.module, len(file.suspicious_usages)))


statistics_format = '''
Statistics:

模块：{}  包：{}  类文件：{}   
依赖数量：{}   引用数量：{}  
可疑依赖数量：{}   可疑引用数量：{}  
'''
rule_format = '''BasSmell-{}：{} '''

p_format = '''包：{} 模块：{} 数量：{}'''

c_format = '''类：{} 包：{} 模块：{} 数量：{}'''
