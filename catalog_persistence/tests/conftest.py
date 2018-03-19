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
def change_service(persistence_config):
    return DatabaseService(
        InMemoryDBManager('changes'),
        'articles'
    )


@pytest.fixture(params=[
    CouchDBManager(
        settings={
            'couchdb.uri': 'http://localhost:5984',
            'couchdb.username': 'admin',
            'couchdb.password': 'password'
        }
    ),
    InMemoryDBManager('changes')
])
def database_service(request):
    return DatabaseService(request.param, 'articles')


@pytest.fixture
def setup(request, persistence_config, database_service):
    def fin():
        databases = ['articles', 'changes']
        for database in databases:
            database_service.db_manager.database = database
            database_service.db_manager.drop_database()
    request.addfinalizer(fin)
