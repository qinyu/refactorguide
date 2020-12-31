#!/usr/bin/env python
from refactorguide.models import Class, Layer, group_class_by_module_package


def test_grouped_by_modules_and_packages():

    sort_by_module = group_class_by_module_package([
        Class(path="", full_name="should.be.first.View",
              package="should.be.first", module="a"),
        Class(path="", full_name="should.be.second.View",
              package="should.be.second", module="b")])
    assert list(sort_by_module.keys()) == ['a', 'b']
    assert 'should.be.first' in sort_by_module['a']
    assert 'should.be.second' in sort_by_module['b']

    sort_by_package = group_class_by_module_package([
        Class(path="", full_name="should.be.first.View",
              package="should.be.first", module="same.module"),
        Class(path="", full_name="should.be.second.View",
              package="should.be.second", module="same.module")])
    assert list(sort_by_package.keys()) == ['same.module']
    assert list(sort_by_package['same.module'].keys()) == [
        'should.be.first', 'should.be.second']

    sort_by_raw_package = group_class_by_module_package([
        Class(path="", full_name="same.package.b.Class2",
              package="same.package", module="same.module"),
        Class(path="", full_name="same.package.a.Class1",
              package="same.package", module="same.module")])
    assert list(sort_by_raw_package.keys()) == ['same.module']
    assert list(sort_by_raw_package['same.module'].keys()) == ['same.package']
    assert [c.name for c in sort_by_raw_package['same.module']
            ['same.package']] == ['a.Class1', 'b.Class2']

    sort_by_class = group_class_by_module_package([
        Class(path="", full_name="same.package.Class1",
              package="same.package", module="same.module"),
        Class(path="", full_name="same.package.Class2",
              package="same.package", module="same.module")])
    assert list(sort_by_class.keys()) == ['same.module']
    assert list(sort_by_class['same.module'].keys()) == ['same.package']
    assert list([c.name for c in sort_by_class['same.module']
                 ['same.package']]) == ['Class1', 'Class2']


def test_layer():
    t = Layer
    assert t("test", list(), **{'layer': 'alayer',
                                'module': 'amodule', 'package': 'apackge'}).name == "test"
