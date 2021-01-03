
from refactorguide.smells import SmellDependency
from refactorguide.hierarchy import build_hierarchy
import pytest
from refactorguide.models import Class

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

http_cls = Class(path='http/src/main/org/http/HttpClient.java',
                 module='http', package='org.http', full_name='org.http.HttpClient')
app_cls = Class(path='app/src/main/com/test/Main.java',
                module='app', package='com.test', full_name='com.test.Main')
log_cls = Class(path='log/src/main/org/log/LoggerHandler.java',
                     module='log', package='org.log', full_name='org.log.LoggerHandler')
page_cls = Class(path='ui/src/main/com/test/ui/ListPageM.java',
                 module='ui', package='com.test.ui', full_name='com.test.ui.ListPage')
unknown_cls = Class(path='3rdparty/src/main/org/junit/Test.java',
                    module='junit', package='org.junit', full_name='org.junit.Test')


@pytest.fixture()
def hierarchy():
    return build_hierarchy([http_cls, app_cls, log_cls,
                            page_cls, unknown_cls], layers)


def test_is_in_layer(hierarchy):

    assert http_cls.is_layer('platform')
    assert log_cls.is_layer('platform')
    assert app_cls.is_layer('app')
    assert page_cls.is_layer('app')
    assert not unknown_cls.is_layer('platform')
    assert not app_cls.is_layer('platform')
    assert not page_cls.is_layer('platform')
    assert not unknown_cls.is_layer('app')
    assert not http_cls.is_layer('app')
    assert not log_cls.is_layer('app')


def test_smell_layer_dependency(hierarchy):
    smell_platform_depend_app = SmellDependency(
        **{'from': 'platform', 'to': 'app'})
    assert smell_platform_depend_app(hierarchy, http_cls, app_cls)
    assert smell_platform_depend_app(hierarchy, log_cls, page_cls)
    assert not smell_platform_depend_app(hierarchy, app_cls, http_cls)
    assert not smell_platform_depend_app(hierarchy, app_cls, http_cls)
    assert not smell_platform_depend_app(hierarchy, http_cls, log_cls)
    assert not smell_platform_depend_app(hierarchy, app_cls, page_cls)


def test_smell_dependency(hierarchy):
    smell_platform_depend_app = SmellDependency(
        **{'from': 'platform', 'to': 'app'})
    assert smell_platform_depend_app(hierarchy, http_cls, app_cls)
    assert smell_platform_depend_app(hierarchy, log_cls, page_cls)
    assert not smell_platform_depend_app(hierarchy, app_cls, http_cls)
    assert not smell_platform_depend_app(hierarchy, app_cls, http_cls)
    assert not smell_platform_depend_app(hierarchy, http_cls, log_cls)
    assert not smell_platform_depend_app(hierarchy, app_cls, page_cls)
