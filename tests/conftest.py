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
        InMemoryDBManager({'database_name': 'test1'}),
        InMemoryDBManager({'database_name': 'test2'})
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
