
# coding=utf-8

from refactorguide.tools import write_file
from refactorguide.models import Hierarchy, group_class_by_module_package


def write_files(report_dir, hierarchy: Hierarchy):
    # dt = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
    for layer in hierarchy.layers:
        for module in layer.modules:
            # build plantuml head
            print("start print "+module.name+"to uml")
            for package in module.packages:
                uml = "@startuml \n\n"
                group_classes = []
                group_dict = {}
                for cls in package.classes:
                    group_classes += cls.smell_dependencies
                    group_classes += cls.smell_usages
                # build plantuml head
                group_dict = group_class_by_module_package(
                    package.classes+group_classes)
                uml += "".join([get_plant_head(module.name, group_pkg_dict)
                                for group_m, group_pkg_dict in group_dict.items()])

                for cls in package.classes:
                    # build plantuml relation
                    uml += get_plant_relation(cls,
                                              cls.smell_dependencies, False)
                    uml += get_plant_relation(cls, cls.smell_usages, True)
                uml += "\n@enduml"
                write_file(report_dir+"/" + module.name + "/" +
                           package.name+"/", package.name+".puml", uml)
            print("end print "+module.name+"to uml")


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
