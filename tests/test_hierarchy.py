
from refactorguide.desgin import LAYER_UNKNOWN
from refactorguide.models import Class, Hierarchy
from refactorguide.hierarchy import add_to, build_hierarchy, filter_hierarchy, remove_from

classes = [Class(path="", full_name="a.package.Class1",
                 package="a.package", module="a"),
           Class(path="", full_name="b.package.subpackage1.Class2",
                 package="b.package.subpackage1", module="b"),
           Class(path="", full_name="b.package.subpackage2.Class3",
                 package="b.package.subpackage2", module="b")]


def test_build_hierarchy_with_useless_wildcards():
    hierarchy = build_hierarchy(classes,
                                {},
                                {})
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': []},
                                {})
    assert_all_in_unknown_layer_and_original_package(hierarchy)
    hierarchy = build_hierarchy(classes,
                                {'lib': [{}]},
                                {})
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
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

    assert_all_in_unknown_layer_and_original_package(hierarchy)


def test_build_hierarchy_with_wrong_wildcards(capsys):
    hierarchy = build_hierarchy(classes,
                                {'lib': [{"no_module_key": "*not.exist"}]},
                                {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'no_module_key': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{"no_module_key": "*not.exist"}]},
                                {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'no_module_key': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{"module_must_be_specified": "a",
                                          "package": "*not.exist"}]},
                                {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'module_must_be_specified': 'a', 'package': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{"module": "a", "package_must_be_specified": "a.package",
                                          "class": "*NotExist"}]},
                                {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing package {'module': 'a', " + \
        "'package_must_be_specified': 'a.package', 'class': '*NotExist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{"module_must_be_specified": "a", "package": "a.package",
                                          "class": "*NotExist"}]},
                                {})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'module_must_be_specified': 'a', " +\
        "'package': 'a.package', 'class': '*NotExist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{}]},
                                {})
    out, _ = capsys.readouterr()
    assert out == 'Warning: missing module {}\n'
    assert_all_in_unknown_layer_and_original_package(hierarchy)


def test_build_hierarchy_with_specified_pacakge():
    hierarchy = build_hierarchy(classes,
                                {},
                                {'b': ['b.package']})

    assert hierarchy[LAYER_UNKNOWN]['b']['b.package'].package == 'b.package'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package']['subpackage1.Class2'].name == 'Class2'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package']['subpackage1.Class2'].package == 'b.package.subpackage1'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package']['subpackage1.Class2'].full_name == 'b.package.subpackage1.Class2'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package']['subpackage2.Class3'].name == 'Class3'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package']['subpackage2.Class3'].package == 'b.package.subpackage2'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package']['subpackage2.Class3'].full_name == 'b.package.subpackage2.Class3'


def test_add_to_hierarchy():
    cls = Class("class/path", "apackage.Class",
                "apackage", "amodule", "alayer")
    other_cls = Class("other/class/path", "apackage.OtherClass",
                      "apackage", "amodule", "alayer")

    hierarchy = add_to(cls, Hierarchy())
    hierarchy = add_to(other_cls, hierarchy)

    assert hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert hierarchy['alayer']['amodule']['apackage']['OtherClass'] == other_cls


def test_remove_from_hierarchy():
    cls = Class("class/path", "apackage.Class",
                "apackage", "amodule", "alayer")
    other_cls = Class("other/class/path", "apackage.OtherClass",
                      "apackage", "amodule", "alayer")

    hierarchy = add_to(cls, Hierarchy())
    hierarchy = add_to(other_cls, hierarchy)

    remove_from(other_cls, hierarchy)
    assert hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert not hierarchy['alayer']['amodule']['apackage']['OtherClass']

    hierarchy = add_to(other_cls, hierarchy)
    remove_from(hierarchy['alayer']['amodule']['apackage'], hierarchy)
    assert not hierarchy.layers

    hierarchy = add_to(cls, hierarchy)
    remove_from(hierarchy['alayer']['amodule'], hierarchy)
    assert not hierarchy.layers

    hierarchy = add_to(cls, hierarchy)
    remove_from(hierarchy['alayer'], hierarchy)
    assert not hierarchy.layers


def test_filter_hierarchy():
    cls = Class("class/path", "apackage.Class",
                "apackage", "amodule", "alayer")
    other_cls = Class("other/class/path", "apackage.OtherClass",
                      "apackage", "amodule", "alayer")

    hierarchy = add_to(cls, Hierarchy())
    hierarchy = add_to(other_cls, hierarchy)

    filtered_hierarchy = filter_hierarchy(
        hierarchy, {"layer": "alayer"}, Hierarchy())
    assert filtered_hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert filtered_hierarchy['alayer']['amodule']['apackage']['OtherClass'] == other_cls

    filtered_hierarchy = filter_hierarchy(
        hierarchy, {}, Hierarchy())
    assert filtered_hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert filtered_hierarchy['alayer']['amodule']['apackage']['OtherClass'] == other_cls

    filtered_hierarchy = filter_hierarchy(
        hierarchy, {"layer": "a*"}, Hierarchy())
    assert filtered_hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert filtered_hierarchy['alayer']['amodule']['apackage']['OtherClass'] == other_cls

    filtered_hierarchy = filter_hierarchy(
        hierarchy, {"layer": "b*"}, Hierarchy())
    assert not filtered_hierarchy.items

    filtered_hierarchy = filter_hierarchy(
        hierarchy, {"layer": "alayer", "package": "apackage"}, Hierarchy())
    assert filtered_hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert filtered_hierarchy['alayer']['amodule']['apackage']['OtherClass'] == other_cls

    filtered_hierarchy = filter_hierarchy(
        hierarchy, {"layer": "alayer", "package": "a*"}, Hierarchy())
    assert filtered_hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert filtered_hierarchy['alayer']['amodule']['apackage']['OtherClass'] == other_cls

    filtered_hierarchy = filter_hierarchy(
        hierarchy, {"layer": "a*", "package": "apackage"}, Hierarchy())
    assert filtered_hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert filtered_hierarchy['alayer']['amodule']['apackage']['OtherClass'] == other_cls

    filtered_hierarchy = filter_hierarchy(
        hierarchy, {"layer": "alayer", "package": "b*"}, Hierarchy())
    assert not filtered_hierarchy.items


def assert_all_in_unknown_layer_and_original_package(hierarchy):
    assert hierarchy[LAYER_UNKNOWN]['a'].layer == LAYER_UNKNOWN

    a_package = hierarchy[LAYER_UNKNOWN]['a']['a.package']
    assert a_package.package == 'a.package'
    assert a_package.module == 'a'
    assert a_package.layer == LAYER_UNKNOWN

    class1 = a_package['Class1']
    assert class1.name == 'Class1'
    assert class1.package == 'a.package'
    assert class1.module == 'a'
    assert class1.layer == LAYER_UNKNOWN

    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage1'].package == 'b.package.subpackage1'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage2'].package == 'b.package.subpackage2'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage1']['Class2'].name == 'Class2'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage2']['Class3'].name == 'Class3'
