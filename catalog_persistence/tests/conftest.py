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
            'couchdb.password': 'password',
            'database_name': 'articles'
        }
    )


@pytest.fixture
def get_inmemorydb_manager(persistence_config):
    return InMemoryDBManager('articles')


@pytest.fixture(params=[
    CouchDBManager(
        settings={
            'couchdb.uri': 'http://localhost:5984',
            'couchdb.username': 'admin',
            'couchdb.password': 'password',
            'database_name': 'articles'
        }
    ),
    InMemoryDBManager('articles')
])
def database_service(request):
    return DatabaseService(request.param)


@pytest.fixture
def setup(request, persistence_config, database_service):
    def fin():
        database_service.collection.drop_database()
    request.addfinalizer(fin)


@pytest.fixture
def document_test():
    create_date = datetime.utcnow()
    return {
        'type': 'A',
        'created_date': create_date,
    }
