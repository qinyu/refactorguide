# coding=utf-8
import time
import os


def console_markdown(module_dict):
    for m, pkg_dict in module_dict.items():
        dt = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        print("start print "+m+"to markdown")
        for p, pkg in pkg_dict.items():
            markdown = get_markdown(m, p, pkg)
            markdown += md_line
            markdown += "# suspicious_dependencies: \n"
            markdown += "".join([md_class_format.format(dep_file.package + "." + dep_file.name)for dep_file in pkg.suspicious_dependencies])
            markdown += md_line
            markdown += "# suspicious_usages: \n"
            markdown += "".join([md_class_format.format(usages_file.package +"." + usages_file.name)for usages_file in pkg.suspicious_usages])
            writeToFile(dt, m, p, markdown)
        print("end print "+m+"to markdown")


def get_markdown(module_name, package_name, pkg):
    result = md_module_format.format(module_name)
    result += md_package_format.format(package_name)
    result += md_line
    result += "".join([md_class_format.format(file.package + "." + file.name) for file in pkg.classes])
    return result


def writeToFile(dt, m, p, uml):
    path = dt+"/"+m
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
md_package_format = "包：{} \n"
md_class_format = "|---{} \n"
md_line="\n"+"--------------------\n"
