
# coding=utf-8
import time
import os
from model import  grouped_by_modules_and_logic_packages


def console_plant_uml(module_dict):
    for m, pkg_dict in module_dict.items():
        # build plantuml head
        dt = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
        print("start print "+m+"to uml")
        for p, pkg in pkg_dict.items():
            uml = "@startuml \n\n"
            group_classes=[]
            group_dict={}
            for file in pkg.classes:
                group_classes+=file.suspicious_dependencies
                group_classes+=file.suspicious_usages
            # build plantuml head    
            group_dict=grouped_by_modules_and_logic_packages(pkg.classes+group_classes)
            uml += "".join([get_plant_head(m, group_pkg_dict) for group_m,group_pkg_dict in group_dict.items()])

            for file in pkg.classes:
                # build plantuml relation         
                uml += get_plant_relation(file,file.suspicious_dependencies, False)
                uml += get_plant_relation(file, file.suspicious_usages, True)
            uml += "\n@enduml"
            writeToFile(dt, m, p, uml)
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
            str.append(uml_relation_format.format(
                file.name, condition, dep_file.name))
        else:
            str.append(uml_back_relation_format.format(
                file.name, condition, dep_file.name))
    return ''.join(str)


def writeToFile(dt, m, p, uml):
    path = "Report_"+dt+"/"+m+"/uml/"
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        print(path+' 创建成功')
    f = open(path+'/'+p+".puml", 'w', encoding='utf-8')
    f.write(''.join(uml))
    f.close()
    print("wirite file succes,output file name is :"+p+".puml")


uml_module_format = "Package {} {{ \n{} }} \n"
uml_package_format = "Package {} {{ \n{}   }} \n"
uml_class_format = "  class {} \n"
uml_relation_format = "{} <|-{}- {}\n"
uml_back_relation_format = "{} -{}-|> {}\n"
