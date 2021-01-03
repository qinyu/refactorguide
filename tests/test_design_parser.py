from refactorguide.design_parser import __read_smells, __read_layers, load_design
import pytest
from configparser import ConfigParser as CP
import os

sample_design = '''
[smells]
  SmellDependencyCrossModule
  SmellDependencyCrossPackage
  SmellCylicDependency
  SmellDependency: [
      {
        "from": {"module": "app", "package": "com.pretty.helper" },
        "to": {"module": "app", "package": "com.data.dao", "name": "NameParser"}
      },
      {"from": "platform", "to": "app"},
      {"from": "service", "to": "app"}
    ]

[layers]
  platform = [
      {"module": "app", "package": "com.pretty.helper"},
      {"path": ":app:com.pretty.util"}
    ]
'''


@pytest.fixture
def config_parser() -> CP:
    cp = CP(allow_no_value=True)
    cp.optionxform = str
    return cp


def test_read_smells(config_parser: CP):
    config_parser.read_string(sample_design)
    smells = __read_smells(config_parser)
    assert [type(s).__name__ for s in smells] == [
        'SmellDependencyCrossModule',
        'SmellDependencyCrossPackage',
        'SmellCylicDependency',
        'SmellDependency',
        'SmellDependency',
        'SmellDependency']


def test_read_layers(config_parser: CP):
    config_parser.read_string(sample_design)
    layers = __read_layers(config_parser)
    assert layers == {'platform': [
        {'module': 'app', 'package': 'com.pretty.helper'},
        {"path": ":app:com.pretty.util"}
    ]}


def test_load_design(tmp_path):
    with open(tmp_path / "design.ini", 'w', encoding='utf-8') as design_file:
        design_file.write(sample_design)

    design = load_design(tmp_path / "design.ini")
    assert [type(s).__name__ for s in design.smells] == [
        'SmellDependencyCrossModule',
        'SmellDependencyCrossPackage',
        'SmellCylicDependency',
        'SmellDependency',
        'SmellDependency',
        'SmellDependency']
    assert design.layers == {'platform': [
        {'module': 'app', 'package': 'com.pretty.helper'},
        {"path": ":app:com.pretty.util"}
    ]}


def test_load_default_design_if_file_not_exist(tmp_path):
    design = load_design(tmp_path / "design.ini")
    assert [type(s).__name__ for s in design.smells] == [
        'SmellDependencyCrossModule',
        'SmellDependencyCrossPackage',
        'SmellCylicDependency']
    assert design.layers == {}
    assert not os.path.exists(tmp_path / "design.ini")


def test_generate_sample_design_if_file_not_exist(tmp_path):
    assert not os.path.exists(tmp_path / "design.ini")
    design = load_design(tmp_path / "design.ini", generate_example=True)
    assert os.path.exists(tmp_path / "design.ini")
    assert [type(s).__name__ for s in design.smells] == [
        'SmellDependencyCrossModule',
        'SmellDependencyCrossPackage',
        'SmellCylicDependency']
    assert design.layers == {}
