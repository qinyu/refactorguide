#!/usr/bin/env python
from refactorguide.models import Class, Dependency, grouped_by_modules_and_packages, update_class_logic_packages, \
    hierachy


def test_grouped_by_modules_and_packages():

    sort_by_module = grouped_by_modules_and_packages([
        Class(path="", name="View", raw_package="should.be.first", module="a"),
        Class(path="", name="View", raw_package="should.be.second", module="b")])
    assert list(sort_by_module.keys()) == ['a', 'b']
    assert 'should.be.first' in sort_by_module['a']
    assert 'should.be.second' in sort_by_module['b']

    sort_by_package = grouped_by_modules_and_packages([
        Class(path="", name="View", raw_package="should.be.first",
              module="same.module"),
        Class(path="", name="View", raw_package="should.be.second", module="same.module")])
    assert list(sort_by_package.keys()) == ['same.module']
    assert list(sort_by_package['same.module'].keys()) == [
        'should.be.first', 'should.be.second']

    sort_by_raw_package = grouped_by_modules_and_packages([
        Class(path="", name="second", raw_package="same.package.b",
              module="same.module", package="same.package"),
        Class(path="", name="first", raw_package="same.package.a", module="same.module", package="same.package")])
    assert list(sort_by_raw_package.keys()) == ['same.module']
    assert list(sort_by_raw_package['same.module'].keys()) == ['same.package']
    assert [c.name for c in sort_by_raw_package['same.module']
            ['same.package']] == ['first', 'second']

    sort_by_class = grouped_by_modules_and_packages([
        Class(path="", name="second",
              raw_package="same.package", module="same.module"),
        Class(path="", name="first", raw_package="same.package", module="same.module")])
    assert list(sort_by_class.keys()) == ['same.module']
    assert list(sort_by_class['same.module'].keys()) == ['same.package']
    assert list([c.name for c in sort_by_class['same.module']
                 ['same.package']]) == ['first', 'second']


def test_update_class_logic_packages():
    cls = Class(path="", name="View",
                raw_package="info.qinyu.biz.ui", module="test")
    cls.dependencies = [
        Dependency(path="", name="Model", raw_package="info.qinyu.biz.model", module="test", category="Production")]
    cls.usages = [
        Dependency(path="", name="App", raw_package="info.qinyu",
                   module="test", category="Production"),
        Dependency(path="", name="Page", raw_package="info.qinyu.biz.ui", module="test", category="Production")]

    # Nothing get updated if empty
    update_class_logic_packages([cls], {})
    assert cls.package == 'info.qinyu.biz.ui'
    assert cls.dependencies[0].package == 'info.qinyu.biz.model'
    assert cls.usages[0].package == 'info.qinyu'
    assert cls.usages[1].package == 'info.qinyu.biz.ui'

    update_class_logic_packages([cls], {'test':  ['info.qinyu.biz']})
    assert cls.package == 'info.qinyu.biz'
    assert cls.dependencies[0].package == 'info.qinyu.biz'
    assert cls.usages[0].package == 'info.qinyu'
    assert cls.usages[1].package == 'info.qinyu.biz'


def test_hierachy():
    _hierachy = hierachy([
        Class(path="", name="Class1", raw_package="a.first.package", module="a"),
        Class(path="", name="Class2", raw_package="b.first.package", module="b"),
        Class(path="", name="Class3", raw_package="b.second.package", module="b")])

    assert list(_hierachy.keys()) == ['a', 'b']
    assert _hierachy['a']['a.first.package'].name == 'a.first.package'
    assert _hierachy['a']['a.first.package']['Class1'].name == 'Class1'

    assert _hierachy['b']['b.first.package'].name == 'b.first.package'
    assert _hierachy['b']['b.second.package'].name == 'b.second.package'
    assert _hierachy['b']['b.first.package']['Class2'].name == 'Class2'
    assert _hierachy['b']['b.second.package']['Class3'].name == 'Class3'
