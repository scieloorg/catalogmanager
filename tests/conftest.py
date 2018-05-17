import os

import couchdb
import pytest
import webtest

from api import main


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
def db_settings():
    return {
        'db_host': 'http://127.0.0.1',
        'db_port': '5984',
        'username': 'admin',
        'password': 'password'
    }


@pytest.fixture
def testapp(request, db_settings):
    settings = {'__file__': 'development.ini'}
    test_app = main(settings)

    def drop_database():
        db_server = couchdb.Server('{}:{}'.format(db_settings['db_host'],
                                                  db_settings['db_port']))
        db_server.resource.credentials = (db_settings['username'],
                                          db_settings['password'])
        try:
            db_server.delete('changes')
            db_server.delete('articles')
        except couchdb.http.ResourceNotFound:
            pass
    request.addfinalizer(drop_database)
    return webtest.TestApp(test_app)
