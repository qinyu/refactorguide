import refactorguide.desgin as design
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
    assert design.LAYERS == {}
    assert design.LOGIC_PACKAGES == {}
    assert [type(s) for s in design.SMELLS] == [
        SmellDependencyCrossModule, SmellDependencyCrossPackage, SmellCylicDependency]


def test_set_layers():
    design.set_layers(layers)
    assert design.LAYERS == layers
