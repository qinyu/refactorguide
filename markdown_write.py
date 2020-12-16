# coding=utf-8
import time
import os
from model import grouped_info,grouped_by_modules_and_logic_packages

def console_markdown(module_dict):
    for m, pkg_dict in module_dict.items():
        dt = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
        print("start print "+m+"to markdown")
        for p, pkg in pkg_dict.items():
            markdown = get_markdown(m, p, pkg)
            markdown += md_line
            markdown += "# suspicious_dependencies: \n"
            markdown += grouped_info(grouped_by_modules_and_logic_packages(pkg.suspicious_dependencies))
            markdown += md_line
            markdown += "# suspicious_usages: \n"
            markdown += grouped_info(grouped_by_modules_and_logic_packages(pkg.suspicious_usages))
            writeToFile(dt, m, p, markdown)
        print("end print "+m+"to markdown")


def get_markdown(module_name, package_name, pkg):
    result = md_module_format.format(module_name)
    result += md_package_format.format(package_name,len(pkg.suspicious_dependencies),len(pkg.suspicious_usages))
    result += md_line
    sort_classes=sorted(pkg.classes,key = sorted_by_dep,reverse=True)
    result += "".join([md_class_format.format(file.package + "." + file.name,len(file.suspicious_dependencies),len(file.suspicious_usages)) for file in sort_classes])
    return result

def sorted_by_dep(file):
    return len(file.suspicious_dependencies)

def writeToFile(dt, m, p, uml):
    path = "Report_"+dt+"/"+m+"/markdown/"
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        print(path+' 创建成功')
    f = open(path+'/'+p+".md", 'w', encoding='utf-8')
    f.write(''.join(uml))
    f.close()
    print("wirite file succes,output file name is :"+p+".md")


md_module_format = "# {} \n"
md_package_format = "包：{}  \n|---dependencies:{} usages:{}\n"
md_class_format = "|---{}   \n|   |---dependencies:{} usages:{} \n"
md_line="\n"+"--------------------\n"