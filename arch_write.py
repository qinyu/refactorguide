# coding=utf-8
import time
import os
from config import *


def to_module_dict(li):
    _module_dict = {}
    for _dict in li:
        m = _dict['module']
        _module_dict[m] = _module_dict.get(m, {})
        if 'package' in _dict.keys():
            p = _dict['package']
            _module_dict[m][p] = _module_dict[m].get(p, [])
            if 'name' in _dict.keys():
                c = _dict['name']
                if c not in _module_dict[m][p]:
                    _module_dict[m][p].append(c)
    return _module_dict


def console_architecture_plant_uml():
    dt = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
    module_dict = {}
    uml = ""
    module_dict = to_module_dict(service)
    # group platform data
    # for item in platform:
    #     module=item.get("module")
    #     package=item.get("package")
    #     module_dict.setdefault(module)
    #     if module_dict.get(module) is None:
    #         module_dict[module]={}
    #     if package is not None:
    #         module_dict.get(module).append(package)
    #     else:
    #         module_dict.get(module).append(package)
    print(module_dict)
    # build uml
    for m, pkg_dict in module_dict.items():
        uml += get_plant_head(m, pkg_dict)
    writeToFile(dt, uml)
    print("end print architecture to uml")


def get_plant_head(module_name, pkg_dict):
    package_str = ""
    for p, v in pkg_dict.items():
        package_str += ''.join([uml_package_format.format(p,
                                                          uml_class_format.format("".join(v)))])
    moudle_str = uml_module_format.format(module_name, package_str)
    return moudle_str


def writeToFile(dt, uml):
    path = "Report_"+dt+"/architecture/"
    os.makedirs(path, exist_ok=True)
    with open(path+'/'+"architecture.puml", 'w', encoding='utf-8') as f:
        f.write(''.join(uml))
    print("wirite architecture succes,output file name is architecture.puml")


uml_module_format = "Package {} {{ \n{} }} \n"
uml_package_format = "Package {} {{  \n{}  }} \n"
uml_class_format = "  class {} \n"


if __name__ == "__main__":
    console_architecture_plant_uml()
