module_list=[]
package_list=[]
class_list=[]

def console_statistics_data(file_list):
    total_dep_count=0
    cross_module_count=0
    cross_package_count=0
    normal_count=0  
    for file in file_list:
        calculator_list(file)
        for dep_file in file.dependencies:
            total_dep_count += 1
            calculator_list(dep_file)
            if dep_file.module!=file.module:
                cross_module_count += 1
            elif dep_file.module==file.module and dep_file.package!=file.package:
                cross_package_count += 1
            elif dep_file.module==file.module and dep_file.package==file.package:
                normal_count += 1
    print(statistics_format.format(len(module_list),len(package_list),len(class_list),total_dep_count,cross_module_count,cross_package_count,normal_count))

statistics_format = '''
Statistics：

Total Module = {} Total Package = {} Total Class ={}  

Total Dependency={}
Cross Module Dependency= {} 
Cross Package Dependency ={} 
Normal Class Dependency={}

'''

def calculator_list(file):
    if(file.module not in module_list):
        module_list.append(file.module)
    if(file.package not in package_list):
        package_list.append(file.package)
    if(file.name not in class_list):
        class_list.append(file.name)