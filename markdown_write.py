# coding=utf-8
import time
import os
from model import grouped_info, grouped_by_modules_and_logic_packages,package_description


def console_markdown(module_dict):
    dt = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
    for m, pkg_dict in module_dict.items():
        # print("start print "+m+"to markdown")
        for p, pkg in pkg_dict.items():
            markdown = get_markdown(m, p, pkg)
            markdown += "\n## 坏味道依赖有{}项:  \n\n".format(len(pkg.suspicious_dependencies))
            markdown += grouped_info(
                grouped_by_modules_and_logic_packages(pkg.suspicious_dependencies))
            markdown += md_line
            markdown += "\n## 坏味道调用有{}处:  \n\n".format(len(pkg.suspicious_usages))
            markdown += grouped_info(
                grouped_by_modules_and_logic_packages(pkg.suspicious_usages))
            writeToFile(m, p, markdown, dt)
        # print("end print "+m+"to markdown")


def get_markdown(module_name, package_name, pkg):
    return package_description(pkg)


def sorted_by_dep(file):
    return len(file.dependencies)

def sorted_by_usage(file):
    return len(file.usages)


def writeToFile(m, p, uml, dt=""):
    path = "Report_"+dt+"/"+m+"/markdown/"
    os.makedirs(path, exist_ok=True)
    with open(path+'/'+p+".md", 'w', encoding='utf-8') as f:
        f.write(''.join(uml))

md_module_format = "# {} \n"
md_package_format = """包：{} 
--------------------  
总共有 {} 项依赖，被调用 {} 处  
--------------------  
"""
md_class_format = "{} (依赖项{},被调用{})\n"
md_line = "\n--------------------\n"
