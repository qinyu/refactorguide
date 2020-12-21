# coding = utf-8s

from smells import ShouldNotDepend, BadSmellCrossModule, BadSmellCrossPackage, BadSmellCylicDependency

logic_pacakges = {
    # 'app':  ['com.fastaccess.ui.modules']
}


dependency_smells = [
    BadSmellCrossModule(),
    BadSmellCrossPackage(),
    BadSmellCylicDependency(),
    ShouldNotDepend(
        {'module': 'app', 'package': 'com.prettifier.pretty.helper', },
        {'module': 'app', 'package': 'com.fastaccess.data.dao', 'name': 'NameParser'}
    )
]

usage_smells = dependency_smells
