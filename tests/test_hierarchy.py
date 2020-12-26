
from refactorguide.desgin import LAYER_UNKNOWN
from refactorguide.models import Class
from refactorguide.hierachy import build_hierachy

classes = [Class(path="", full_name="a.package.Class1",
                 package="a.package", module="a"),
           Class(path="", full_name="b.package.subpackage1.Class2",
                 package="b.package.subpackage1", module="b"),
           Class(path="", full_name="b.package.subpackage2.Class3",
                 package="b.package.subpackage2", module="b")]


def test_build_hierachy_with_useless_wildcards():
    hierachy = build_hierachy(classes,
                              {},
                              {})
    assert_all_in_unknown_layer_and_original_package(hierachy)

    hierachy = build_hierachy(classes,
                              {'lib': []},
                              {})
    assert_all_in_unknown_layer_and_original_package(hierachy)
    hierachy = build_hierachy(classes,
                              {'lib': [{}]},
                              {})
    assert_all_in_unknown_layer_and_original_package(hierachy)

    hierachy = build_hierachy(classes,
                              {'lib': [
                                  {"module": "not.exist"},
                                  {"module": "a", "package": "not.exist"},
                                  {"module": "a", "package": "a.package",
                                   "class": "NotExist"},
                                  {"module": "*not.exist"},
                                  {"module": "a", "package": "*not.exist"},
                                  {"module": "a", "package": "a.package",
                                   "class": "*NotExist"}
                              ]},
                              {})

    assert_all_in_unknown_layer_and_original_package(hierachy)


def test_build_hierachy_with_wrong_wildcards(capsys):
    hierachy = build_hierachy(classes,
                              {'lib': [{"no_module_key": "*not.exist"}]},
                              {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'no_module_key': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierachy)

    hierachy = build_hierachy(classes,
                              {'lib': [{"no_module_key": "*not.exist"}]},
                              {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'no_module_key': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierachy)

    hierachy = build_hierachy(classes,
                              {'lib': [{"module_must_be_specified": "a",
                                        "package": "*not.exist"}]},
                              {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'module_must_be_specified': 'a', 'package': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierachy)

    hierachy = build_hierachy(classes,
                              {'lib': [{"module": "a", "package_must_be_specified": "a.package",
                                        "class": "*NotExist"}]},
                              {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing package {'module': 'a', " + \
        "'package_must_be_specified': 'a.package', 'class': '*NotExist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierachy)

    hierachy = build_hierachy(classes,
                              {'lib': [{"module_must_be_specified": "a", "package": "a.package",
                                        "class": "*NotExist"}]},
                              {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'module_must_be_specified': 'a', " +\
        "'package': 'a.package', 'class': '*NotExist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierachy)

    hierachy = build_hierachy(classes,
                              {'lib': [{}]},
                              {})
    out, _ = capsys.readouterr()
    assert out == 'Warning: missing module {}\n'
    assert_all_in_unknown_layer_and_original_package(hierachy)


def test_build_hierarchy_with_specified_pacakge():
    hierachy = build_hierachy(classes,
                              {},
                              {'b': ['b.package']})

    assert hierachy[LAYER_UNKNOWN]['b']['b.package'].package == 'b.package'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package']['subpackage1.Class2'].name == 'Class2'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package']['subpackage1.Class2'].package == 'b.package.subpackage1'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package']['subpackage1.Class2'].full_name == 'b.package.subpackage1.Class2'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package']['subpackage2.Class3'].name == 'Class3'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package']['subpackage2.Class3'].package == 'b.package.subpackage2'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package']['subpackage2.Class3'].full_name == 'b.package.subpackage2.Class3'


def assert_all_in_unknown_layer_and_original_package(hierachy):
    assert hierachy[LAYER_UNKNOWN]['a'].layer == LAYER_UNKNOWN

    a_package = hierachy[LAYER_UNKNOWN]['a']['a.package']
    assert a_package.package == 'a.package'
    assert a_package.module == 'a'
    assert a_package.layer == LAYER_UNKNOWN

    class1 = a_package['Class1']
    assert class1.name == 'Class1'
    assert class1.package == 'a.package'
    assert class1.module == 'a'
    assert class1.layer == LAYER_UNKNOWN

    assert hierachy[LAYER_UNKNOWN]['b']['b.package.subpackage1'].package == 'b.package.subpackage1'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package.subpackage2'].package == 'b.package.subpackage2'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package.subpackage1']['Class2'].name == 'Class2'
    assert hierachy[LAYER_UNKNOWN]['b']['b.package.subpackage2']['Class3'].name == 'Class3'
