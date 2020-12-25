
# coding=utf-8

from typing import Dict
from refactorguide.tools import write_file
from refactorguide.models import Module, grouped_by_modules_and_packages


def write_files(report_dir, module_dict: Dict[str, Module]):
    # dt = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
    for m, module in module_dict.items():
        # build plantuml head
        print("start print "+m+"to uml")
        for pkg in module.packages:
            uml = "@startuml \n\n"
            group_classes = []
            group_dict = {}
            for file in pkg.classes:
                group_classes += file.smell_dependencies
                group_classes += file.smell_usages
            # build plantuml head
            group_dict = grouped_by_modules_and_packages(
                pkg.classes+group_classes)
            uml += "".join([get_plant_head(m, group_pkg_dict)
                            for group_m, group_pkg_dict in group_dict.items()])

            for file in pkg.classes:
                # build plantuml relation
                uml += get_plant_relation(file,
                                          file.smell_dependencies, False)
                uml += get_plant_relation(file, file.smell_usages, True)
            uml += "\n@enduml"
            write_file(report_dir+"/" + m + "/" +
                       pkg.name+"/", pkg.name+".puml", uml)
        print("end print "+m+"to uml")


def get_plant_head(module_name, pkg_dict):
    package_str = ""
    for p, classes in pkg_dict.items():
        package_str += ''.join([uml_package_format.format(p, ''.join(
            [uml_class_format.format(file.name) for file in classes]))])
    moudle_str = uml_module_format.format(module_name, package_str)
    return moudle_str


def get_plant_relation(file, dep_file_name_list, isUsage):
    str = []
    condition = ""
    # target uml line level
    for dep_file in dep_file_name_list:
        if dep_file.module != file.module:
            condition = "[#red]"
        elif dep_file.module == file.module and dep_file.package == file.package:
            condition = "[#green]"
        elif dep_file.module == file.module and dep_file.package != file.package:
            condition = "[#blue]"
        else:
            condition = ""
        if(isUsage):
            str.append(uml_relation_format.format(file.name, condition, dep_file.name,
                                                  " :"+"".join([bs.description for bs in dep_file.bad_smells])))
        else:
            str.append(uml_back_relation_format.format(file.name, condition, dep_file.name,
                                                       " :"+"".join([bs.description for bs in dep_file.bad_smells])))
    return ''.join(str)


uml_module_format = "Package {} {{ \n{} }} \n"
uml_package_format = "Package {} {{ \n{}   }} \n"
uml_class_format = "  class {} \n"
uml_relation_format = "{} <|-{}- {} {}\n"
uml_back_relation_format = "{} -{}-|> {} {}\n"
