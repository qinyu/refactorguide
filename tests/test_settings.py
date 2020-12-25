import refactorguide.desgin as desgin
from refactorguide.smells import SmellCylicDependency, SmellDependencyCrossModule, SmellDependencyCrossPackage

platform = [
    {'module': 'http', 'package': '*'},
    {'module': 'log', 'package': 'org.log', 'class': 'Logger*'}
]

app = [
    {'module': 'app', 'package': '*'},
    {'module': 'ui', 'package': 'com.test.ui', 'class': '*Page'}
]

layers = {
    'platform': platform,
    'app': app
}


def test_default_values():
    assert desgin.LAYERS == {}
    assert desgin.LOGIC_PACKAGES == {}
    assert [type(s) for s in desgin.SMELLS] == [
        SmellDependencyCrossModule, SmellDependencyCrossPackage, SmellCylicDependency]


def test_set_layers():
    desgin.set_layers(layers)
    assert desgin.LAYERS == layers
