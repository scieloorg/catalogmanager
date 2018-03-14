from datetime import datetime

from pyramid import testing
import pytest

from catalog_persistence.databases import (
    CouchDBManager,
    InMemoryDBManager,
    DatabaseService
)


@pytest.yield_fixture
def persistence_config(request):
    yield testing.setUp()
    testing.tearDown()


@pytest.fixture
def get_inmemory_manager(persistence_config):
    store = InMemoryDBManager()
    return DatabaseService(store)


@pytest.fixture
def fake_change_list():
    return ['Test1', 'Test2', 'Test3', 'Test4', 'Test5', 'Test6']


@pytest.fixture
def change_service_list(change_service, fake_change_list):
    for description in fake_change_list:
        change_service.register(description)
    return change_service


@pytest.fixture
def get_couchdb_manager(request, persistence_config):
    return CouchDBManager(
        settings={
            'couchdb.uri': 'http://localhost:5984',
            'couchdb.username': 'admin',
            'couchdb.password': 'password'
        }
    )


@pytest.fixture
def database_service(get_couchdb_manager):
    return DatabaseService(get_couchdb_manager)


@pytest.fixture
def setup(request, persistence_config, get_couchdb_manager):
    def fin():
        get_couchdb_manager.drop_database()
    request.addfinalizer(fin)


@pytest.fixture
def document_test():
    create_date = datetime.utcnow()
    return {
        'type': 'A',
        'created_date': create_date,
    }
