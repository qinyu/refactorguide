# coding = utf-8s

from smells import BadSmell, ShouldNotDepend, smell_cross_module, smell_cross_package, smell_cylic_dependency

logic_pacakges = {
    # 'app':  ['com.fastaccess.ui.modules']
}


dependency_smells = [
    BadSmell(smell_cross_module, "此依赖关系跨模块，需进一步分析"),
    BadSmell(smell_cross_package, "此依赖关系跨包，需进一步分析"),
    BadSmell(smell_cylic_dependency, "此依赖是循环依赖，应当解除"),
    ShouldNotDepend(
        {'module': 'app', 'logic_package': 'com.prettifier.pretty.helper', },
        {'module': 'app', 'logic_package': 'com.fastaccess.data.dao', 'name': 'NameParser'}
    )
]

usage_smells = dependency_smells
