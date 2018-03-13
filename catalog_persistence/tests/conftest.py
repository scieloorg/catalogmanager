#!/usr/bin/python
from pyramid import testing
import pytest

from catalog_persistence.couchdb import CouchDBManager
from catalog_persistence.changes import ChangeInMemory, ChangeService


@pytest.yield_fixture
def persistence_config(request):
    yield testing.setUp()
    testing.tearDown()


@pytest.fixture
def change_service(persistence_config):
    store = ChangeInMemory()
    return ChangeService(store)


@pytest.fixture
def fake_change_list():
    return ['Test1', 'Test2', 'Test3', 'Test4', 'Test5', 'Test6']


@pytest.fixture
def change_service_list(change_service, fake_change_list):
    for description in fake_change_list:
        change_service.register(description)
    return change_service


@pytest.fixture
def get_database_manager(request):
    return CouchDBManager(
        settings={
            'couchdb.uri': 'http://localhost:5984',
            'couchdb.db_name': 'catalog_manager',
            'couchdb.username': 'admin',
            'couchdb.password': 'password'
        }
    )


@pytest.fixture
def setup(request, persistence_config, get_database_manager):
    def fin():
        get_database_manager.drop_database()
    request.addfinalizer(fin)
