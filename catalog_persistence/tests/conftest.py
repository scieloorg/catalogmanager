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
def db_settings():
    return {
        'couchdb.uri': 'http://localhost:5984',
        'couchdb.username': 'admin',
        'couchdb.password': 'password'
    }


@pytest.fixture(params=[
    CouchDBManager,
    InMemoryDBManager
])
def database_service(request, db_settings):
    return DatabaseService(
        request.param(db_settings),
        'articles',
        request.param(db_settings)
    )


@pytest.fixture
def setup(request, persistence_config, database_service):
    def fin():
        database_service.db_manager.drop_database()
        database_service.changes_db_manager.drop_database()
    request.addfinalizer(fin)
