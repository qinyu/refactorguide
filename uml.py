import time

def console_plant_uml(file_list):
    print("start print uml")
    module_dict={}
    package_dict={}
    uml=""
    ## build module and package map relation
    for file in file_list:
        if(module_dict.get(file.module)):
            if(module_dict.get(file.module).count(file.package)<=0):
                module_dict.get(file.module).append(file.package)
        else:
            module_dict[file.module]=[file.package]

        if(package_dict.get(file.package)):
            if(package_dict.get(file.package).count(file.name)<=0):
                package_dict.get(file.package).append(file.name)
        else:
            package_dict[file.package]=[file.name]

    for (k,v) in  module_dict.items(): 
        # build plantuml head
        uml+=get_plant_head(k,v,package_dict)
    for file in file_list:
        # build plantuml relation
        uml+=get_plant_relation(file,file.dependencies)
    writeToFile(uml)
    print("end print uml")
            
def get_plant_head(module_name,package_name_list,package_dict):
    package_str=""
    for package_name in package_name_list:
         package_str+=''.join([uml_package_format.format(package_name,''.join([uml_class_format.format(file_name) for file_name in package_dict[package_name]]))])
    moudle_str=uml_module_format.format(module_name,package_str)
    return moudle_str

def get_plant_relation(file,dep_file_name_list):
    str=[]
    condition=""
    # target uml line level
    for dep_file in dep_file_name_list:
        if dep_file.module!=file.module:
            condition="[#red]"
        elif dep_file.module==file.module and dep_file.package==file.package:
            condition="[#green]"
        elif dep_file.module==file.module and dep_file.package!=file.package:
                condition="[#blue]"
        else:
            condition=""
        str.append(uml_relation_format.format(dep_file.name,condition,file.name))
    return ''.join(str)
        
def writeToFile(uml):
    print(uml)
    dt= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    f=open(dt+'.puml','w',encoding='utf-8')
    f.write(''.join(uml))
    f.close()
    print("wirite file succes,output file name is :"+dt)

uml_module_format = "Package {} {{ \n{} }} \n"
uml_package_format = "Package {} {{ \n{}   }} \n"
uml_class_format="  class {} \n"
uml_relation_format="{} <|-{}- {}\n"
