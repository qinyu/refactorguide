# coding=utf-8
import time
import os
from model import BASE, PKG, class_description, grouped_info, grouped_by_modules_and_logic_packages, package_description


def smells_markdown_depscription(base: BASE):
    md = "\n## 坏味道依赖有{}项:  \n\n".format(
        len(base.suspicious_dependencies))
    md += grouped_info(
        grouped_by_modules_and_logic_packages(base.suspicious_dependencies))
    md += md_line
    md += "\n## 坏味道调用有{}处:  \n\n".format(len(base.suspicious_usages))
    md += grouped_info(
        grouped_by_modules_and_logic_packages(base.suspicious_usages))
    return md


def console_markdown(module_dict: dict[str: dict[str:PKG]]):
    dt = time.strftime("%Y%m%d-%H-%M", time.localtime())
    report_dir = "Report_"+dt+"/"
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            export_to_file(report_dir + m + "/markdown/" + p + "/", "_pacakge_.md",
                           package_description(pkg) + smells_markdown_depscription(pkg))
            for cls in pkg.classes:
                export_to_file(report_dir + m + "/markdown/" + p + "/",  cls.full_name +
                               ".md", class_description(cls) + smells_markdown_depscription(cls))


def export_to_file(dir, file, md_content):
    os.makedirs(dir, exist_ok=True)
    with open(dir + "/" + file, 'w', encoding='utf-8') as f:
        f.write(''.join(md_content))


md_module_format = "# {} \n"
md_package_format = """包：{} 
--------------------  
总共有 {} 项依赖，被调用 {} 处  
--------------------  
"""
md_class_format = "{} (依赖项{},被调用{})\n"
md_line = "\n--------------------\n"
