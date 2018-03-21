import pytest
from pyramid import testing
from webtest import TestApp

from catalog_persistence import main
from catalog_persistence.databases import InMemoryDBManager, DatabaseService


@pytest.yield_fixture
def functional_config(request):
    yield testing.setUp()
    testing.tearDown()


@pytest.fixture
def change_service(functional_config):
    return DatabaseService(
        InMemoryDBManager('test1'),
        'test',
        InMemoryDBManager('test2')
    )


@pytest.fixture
def testapp(functional_config):
    settings = {
        'couchdb.uri': 'http://localhost:5984',
        'couchdb.db_name': 'catalog_manager',
        'couchdb.username': 'admin',
        'couchdb.password': 'password',
    }
    test_app = main(settings)
    return TestApp(test_app)
