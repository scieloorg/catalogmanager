import os

import pytest
import webtest
from pyramid import testing

from catalog_persistence.databases import (
    CouchDBManager,
    DatabaseService
)
from catalogmanager_api import main


FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
    )


PKG_A = [
    os.path.join(
        FIXTURE_DIR,
        '741a',
        '0034-8910-rsp-S01518-87872016050006741.xml'
    ),
    os.path.join(
        FIXTURE_DIR,
        '741a',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg'
    ),
    os.path.join(
        FIXTURE_DIR,
        '741a',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    ),
]


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
        CouchDBManager(**articles_database_config),
        CouchDBManager(**changes_database_config)
    )


@pytest.fixture
def setup_couchdb(request, functional_config, dbserver_service):
    database_service = DatabaseService(dbserver_service[0],
                                       dbserver_service[1])

    def fin():
        database_service.db_manager.drop_database()
        database_service.changes_db_manager.drop_database()
    request.addfinalizer(fin)
