from refactorguide.design_parser import read_logic_pacakges, read_smells, read_layers
import pytest
from configparser import ConfigParser as CP

sample_design = '''
[logic packages]
  app: ["com.pretty.helper", "com.data.dao.converters"]
  Test: ["com.pretty.helper.test"]

[bad smells]
  SmellDependencyCrossModule
  SmellDependencyCrossPackage
  SmellCylicDependency
  SmellDependency: [
      {
        "from": {"module": "app", "package": "com.pretty.helper" },
       "to": {"module": "app", "package": "com.data.dao", "name": "NameParser"}
      }
    ]

[layers]
  platform = [
      { "module": "app", "package": "com.pretty.helper" }
    ]
'''


@pytest.fixture
def config_parser() -> CP:
    cp = CP(allow_no_value=True)
    cp.optionxform = str
    return cp


def test_read_logic_packages(config_parser: CP):
    config_parser.read_string(sample_design)
    logic_packages = read_logic_pacakges(config_parser)
    assert logic_packages == {'app': ['com.pretty.helper', 'com.data.dao.converters'],
                              'Test': ['com.pretty.helper.test']}


def test_read_smells(config_parser: CP):
    config_parser.read_string(sample_design)
    smells = read_smells(config_parser)
    assert [type(s).__name__ for s in smells] == ['SmellDependencyCrossModule', 'SmellDependencyCrossPackage',
                                                  'SmellCylicDependency', 'SmellDependency']


def test_read_layers(config_parser: CP):
    config_parser.read_string(sample_design)
    layers = read_layers(config_parser)
    assert layers == {'platform': [
        {'module': 'app', 'package': 'com.pretty.helper'}]}
