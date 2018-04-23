import os

import pytest
import webtest
from pyramid import testing

from catalog_persistence.databases import InMemoryDBManager
from catalog_persistence.services import DatabaseService
from catalogmanager_api import main


@pytest.fixture
def test_fixture_dir():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'test_files',
    )


@pytest.fixture
def test_package_A(test_fixture_dir):
    filenames = (
        '0034-8910-rsp-S01518-87872016050006741.xml',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    )
    return tuple(
        os.path.join(test_fixture_dir, '741a', filename)
        for filename in filenames
    )


@pytest.fixture
def testapp():
    settings = {'__file__': 'development.ini'}
    test_app = main(settings)
    return webtest.TestApp(test_app)


@pytest.yield_fixture
def functional_config(request):
    yield testing.setUp()
    testing.tearDown()


@pytest.fixture
def database_config():
    return {
        'db_host': 'http://127.0.0.1',
        'db_port': '5984',
        'username': 'admin',
        'password': 'password'
    }


@pytest.fixture
def dbserver_service(functional_config, database_config):
    couchdb_config = {
        'database_uri': '{}:{}'.format(
            database_config['db_host'],
            database_config['db_port']
        ),
        'database_username': database_config['username'],
        'database_password': database_config['password'],
    }

    articles_database_config = couchdb_config.copy()
    articles_database_config['database_name'] = "articles"
    changes_database_config = couchdb_config.copy()
    changes_database_config['database_name'] = "changes"
    return (
        InMemoryDBManager(**articles_database_config),
        InMemoryDBManager(**changes_database_config)
    )


@pytest.fixture
def setup_db(request, functional_config, dbserver_service):
    database_service = DatabaseService(dbserver_service[0],
                                       dbserver_service[1])

    def fin():
        database_service.db_manager.drop_database()
        database_service.changes_db_manager.drop_database()
    request.addfinalizer(fin)
