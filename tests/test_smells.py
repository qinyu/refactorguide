
import pytest
from refactorguide.smells import SmellLayerDependency, is_layer
from refactorguide.models import Class
import refactorguide.desgin as design

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
                 module='http', raw_package='org.http', name='HttpClient')
app_cls = Class(path='app/src/main/com/test/Main.java',
                module='app', raw_package='com.test', name='Main')
log_cls = Class(path='log/src/main/org/log/LoggerHandler.java',
                     module='log', raw_package='org.log', name='LoggerHandler')
page_cls = Class(path='ui/src/main/com/test/ui/ListPageM.java',
                 module='ui', raw_package='com.test.ui', name='ListPage')
unkown_cls = Class(path='3rdparty/src/main/org/junit/Test.java',
                   module='junit', raw_package='org.junit', name='Test')


@pytest.fixture()
def setup_layers():
    design.set_layers(layers)


def test_is_in_layer(setup_layers):
    assert is_layer(http_cls, 'platform')
    assert is_layer(log_cls, 'platform')
    assert is_layer(app_cls, 'app')
    assert is_layer(page_cls, 'app')
    assert not is_layer(unkown_cls, 'platform')
    assert not is_layer(app_cls, 'platform')
    assert not is_layer(page_cls, 'platform')
    assert not is_layer(unkown_cls, 'app')
    assert not is_layer(http_cls, 'app')
    assert not is_layer(log_cls, 'app')


def test_smell_layer_dependency(setup_layers):
    smell_platform_depend_app = SmellLayerDependency(
        **{'from': 'platform', 'to': 'app'})
    assert smell_platform_depend_app(http_cls, app_cls)
    assert smell_platform_depend_app(log_cls, page_cls)
    assert not smell_platform_depend_app(app_cls, http_cls)
    assert not smell_platform_depend_app(app_cls, http_cls)
    assert not smell_platform_depend_app(http_cls, log_cls)
    assert not smell_platform_depend_app(app_cls, page_cls)


# def test_smell_dependency():
#     assert smell_platform_depend_app(http_cls, app_cls)
#     assert smell_platform_depend_app(log_cls, page_cls)
#     assert not smell_platform_depend_app(app_cls, http_cls)
#     assert not smell_platform_depend_app(app_cls, http_cls)
#     assert not smell_platform_depend_app(http_cls, log_cls)
#     assert not smell_platform_depend_app(app_cls, page_cls)


# def test_smell_dependency():
#     smell_platform_depend_app = SmellLayerDependency(
#         **{'from': 'platform', 'to': 'app'})
#     assert smell_platform_depend_app(http_cls, app_cls)
#     assert smell_platform_depend_app(log_cls, page_cls)
#     assert not smell_platform_depend_app(app_cls, http_cls)
#     assert not smell_platform_depend_app(app_cls, http_cls)
#     assert not smell_platform_depend_app(http_cls, log_cls)
#     assert not smell_platform_depend_app(app_cls, page_cls)
