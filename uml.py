def console_plant_uml(file_list):
    print("start print uml")
    map={}
    for file in file_list:
        if(map.get(file.package)):
            map.get(file.package).append(file.name)
        else:
            map[file.package]=[file.name]
    for (k,v) in  map.items(): 
        get_plant_head(k,v)
    for file in file_list:
        get_plant_relation(file.name,file.dependencies)
    print("end print uml")
            
def get_plant_head(package_name,file_name_list):
    str=[uml_class_format.format(file_name) for file_name in file_name_list]
    print(uml_package_format.format(package_name,''.join(str)))

def get_plant_relation(file_name,dep_file_name_list):
    depStr=[]
    for dep_file in dep_file_name_list:
        depStr.append(dep_file.name)
    str=[uml_relation_format.format(dep_file_name,file_name) for dep_file_name in depStr]
    print(''.join(str))

uml_package_format = "Package {} {{ \n{} }}"
uml_class_format="  class {} \n"
uml_relation_format="{} <|-- {}\n"
