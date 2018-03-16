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
            'couchdb.password': 'password',
            'couchdb.changes_database': 'changes'
        }
    ),
    InMemoryDBManager('changes')
])
def database_service(request):
    return DatabaseService(request.param, 'articles')


@pytest.fixture
def setup(request, persistence_config, database_service):
    def fin():
        database_service.collection.drop_database()
    request.addfinalizer(fin)
