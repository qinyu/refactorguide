
from refactorguide.desgin import LAYER_UNKNOWN
from refactorguide.models import Class, Hierarchy
from refactorguide.hierarchy import __add_to, build_hierarchy, filter_hierarchy, __remove_from

classes = [Class(path="", name="Class1",
                 package="a.package", module="a"),
           Class(path="", name="Class2",
                 package="b.package.subpackage1", module="b"),
           Class(path="", name="Class3",
                 package="b.package.subpackage2", module="b")]


def test_build_hierarchy_with_useless_wildcards():
    hierarchy = build_hierarchy(classes, {})
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes, {'lib': []})
    assert_all_in_unknown_layer_and_original_package(hierarchy)
    hierarchy = build_hierarchy(classes, {'lib': [{}]})
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
                                ]})

    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [
                                    {"path": ":not.exist"},
                                    {"path": ":a:not.exist"},
                                    {"path": ":a:a.package:NotExist"},
                                    {"path": ":*not.exist"},
                                    {"path": ":a:*not.exist"},
                                    {"path": ":a:a.package:*NotExist"}
                                ]})

    assert_all_in_unknown_layer_and_original_package(hierarchy)


def test_build_hierarchy_with_wrong_wildcards(capsys):
    hierarchy = build_hierarchy(classes,
                                {'lib': [{"no_module_key": "*not.exist"}]})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'no_module_key': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{"no_module_key": "*not.exist"}]})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'no_module_key': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{"module_must_be_specified": "a",
                                          "package": "*not.exist"}]})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'module_must_be_specified': 'a', 'package': '*not.exist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{"module": "a", "package_must_be_specified": "a.package",
                                          "class": "*NotExist"}]})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing package {'module': 'a', " + \
        "'package_must_be_specified': 'a.package', 'class': '*NotExist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes,
                                {'lib': [{"module_must_be_specified": "a", "package": "a.package",
                                          "class": "*NotExist"}]})
    out, _ = capsys.readouterr()
    assert out == "Warning: missing module {'module_must_be_specified': 'a', " +\
        "'package': 'a.package', 'class': '*NotExist'}\n"
    assert_all_in_unknown_layer_and_original_package(hierarchy)

    hierarchy = build_hierarchy(classes, {'lib': [{}]},)
    out, _ = capsys.readouterr()
    assert out == 'Warning: missing module {}\n'
    assert_all_in_unknown_layer_and_original_package(hierarchy)


def test_build_hierarchy_with_specified_pacakge():
    hierarchy = build_hierarchy(classes, {})

    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage1'].package == 'b.package.subpackage1'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage1']['Class2'].name == 'Class2'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage1']['Class2'].package == 'b.package.subpackage1'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage1']['Class2'].full_name == 'b.package.subpackage1.Class2'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage2']['Class3'].name == 'Class3'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage2']['Class3'].package == 'b.package.subpackage2'
    assert hierarchy[LAYER_UNKNOWN]['b']['b.package.subpackage2']['Class3'].full_name == 'b.package.subpackage2.Class3'


def test_add_to_hierarchy():
    cls = Class("class/path", "Class",
                "apackage", "amodule", "alayer")
    other_cls = Class("other/class/path", "OtherClass",
                      "apackage", "amodule", "alayer")

    hierarchy = __add_to(cls, Hierarchy())
    hierarchy = __add_to(other_cls, hierarchy)

    assert hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert hierarchy['alayer']['amodule']['apackage']['OtherClass'] == other_cls


def test_remove_from_hierarchy():
    cls = Class("class/path", "Class",
                "apackage", "amodule", "alayer")
    other_cls = Class("other/class/path", "OtherClass",
                      "apackage", "amodule", "alayer")

    hierarchy = __add_to(cls, Hierarchy())
    hierarchy = __add_to(other_cls, hierarchy)

    __remove_from(other_cls, hierarchy)
    assert hierarchy['alayer']['amodule']['apackage']['Class'] == cls
    assert not hierarchy['alayer']['amodule']['apackage']['OtherClass']

    hierarchy = __add_to(other_cls, hierarchy)
    __remove_from(hierarchy['alayer']['amodule']['apackage'], hierarchy)
    assert not hierarchy.layers

    hierarchy = __add_to(cls, hierarchy)
    __remove_from(hierarchy['alayer']['amodule'], hierarchy)
    assert not hierarchy.layers

    hierarchy = __add_to(cls, hierarchy)
    __remove_from(hierarchy['alayer'], hierarchy)
    assert not hierarchy.layers


def test_filter_hierarchy():
    cls = Class("class/path", "Class",
                "apackage", "amodule", "alayer")
    other_cls = Class("other/class/path", "OtherClass",
                      "apackage", "amodule", "alayer")

    hierarchy = __add_to(cls, Hierarchy())
    hierarchy = __add_to(other_cls, hierarchy)

    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, {}, Hierarchy()), cls, other_cls)
    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, "", Hierarchy()), cls, other_cls)

    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, {"layer": "alayer"}, Hierarchy()), cls, other_cls)
    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, "alayer", Hierarchy()), cls, other_cls)

    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, {"layer": "a*"}, Hierarchy()), cls, other_cls)
    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, "a*", Hierarchy()), cls, other_cls)

    assert not filter_hierarchy(
        hierarchy, {"layer": "b*"}, Hierarchy()).items
    assert not filter_hierarchy(
        hierarchy, "b*", Hierarchy()).items

    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, {"layer": "alayer", "module": "*", "package": "apackage"}, Hierarchy()), cls, other_cls)
    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, "alayer:*:apackage", Hierarchy()), cls, other_cls)

    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, {"layer": "alayer", "module": "*", "package": "a*"}, Hierarchy()), cls, other_cls)
    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, "alayer:*:a*", Hierarchy()), cls, other_cls)

    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, {"layer": "a*", "module": "*", "package": "apackage"}, Hierarchy()), cls, other_cls)
    assert_all_classes_in_hierarchy(filter_hierarchy(
        hierarchy, "a*:*:apackage", Hierarchy()), cls, other_cls)

    assert not filter_hierarchy(
        hierarchy, {"layer": "alayer", "module": "*", "package": "b*"}, Hierarchy()).items
    assert not filter_hierarchy(
        hierarchy, "alayer:b*:*", Hierarchy()).items


def assert_all_classes_in_hierarchy(filtered_hierarchy, *classes):
    for cls in classes:
        assert filtered_hierarchy[cls.layer][cls.module][cls.package][cls.name] == cls


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
