import os

import couchdb
import pytest
import webtest
from pyramid.paster import get_appsettings

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
    return get_appsettings('development.ini')


@pytest.fixture
def testapp(request, db_settings):
    test_app = main({}, **db_settings)

    def drop_database():
        db_server = couchdb.Server('{}:{}'.format(
            db_settings['catalogmanager.db.host'],
            db_settings['catalogmanager.db.port'])
        )
        db_server.resource.credentials = (
            db_settings['catalogmanager.db.username'],
            db_settings['catalogmanager.db.password']
        )
        try:
            db_server.delete('changes')
            db_server.delete('changes_seqnum')
            db_server.delete('articles')
        except couchdb.http.ResourceNotFound:
            pass
    request.addfinalizer(drop_database)
    return webtest.TestApp(test_app)
