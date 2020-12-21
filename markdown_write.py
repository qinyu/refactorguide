# coding=utf-8
import os
from utils import export_to_file
from formatters import class_description, package_description
from model import BASE, PKG, grouped_by_modules_and_logic_packages, grouped_info


def smells_markdown_depscription(base: BASE):
    md = "\n## 坏味道依赖有{}项:  \n\n".format(
        len(base.suspicious_dependencies))
    md += grouped_info(
        grouped_by_modules_and_logic_packages(base.suspicious_dependencies), oneline_format="[{full_name}](../{logic_package}/{full_name}.md)")
    md += md_line
    md += "\n## 坏味道调用有{}处:  \n\n".format(len(base.suspicious_usages))
    md += grouped_info(
        grouped_by_modules_and_logic_packages(base.suspicious_usages), oneline_format="[{full_name}](../{logic_package}/{full_name}.md)")
    return md


def console_markdown(report_dir, module_dict: dict[str: dict[str:PKG]]):
    for m, pkg_dict in module_dict.items():
        for p, pkg in pkg_dict.items():
            export_to_file(os.path.join(report_dir, m, p), "_pacakge_.md",
                           package_description(pkg) + smells_markdown_depscription(pkg))
            for cls in pkg.classes:
                export_to_file(os.path.join(report_dir, m, p),  cls.full_name +
                               ".md", class_description(cls) + smells_markdown_depscription(cls))


md_line = "\n--------------------\n"
