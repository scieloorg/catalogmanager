import os
import pytest
from pyramid import testing
from webtest import TestApp

from catalog_persistence import main
from catalog_persistence.databases import InMemoryDBManager, DatabaseService


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

PKG_B = [
    os.path.join(
        FIXTURE_DIR,
        '741b',
        '0034-8910-rsp-S01518-87872016050006741.xml'
    ),
    os.path.join(
        FIXTURE_DIR,
        '741b',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg'
    ),
    os.path.join(
        FIXTURE_DIR,
        '741b',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    ),
]


PKG_C = [
    os.path.join(
        FIXTURE_DIR,
        '741c',
        '0034-8910-rsp-S01518-87872016050006741.xml'
    ),
    os.path.join(
        FIXTURE_DIR,
        '741c',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg'
    ),
    os.path.join(
        FIXTURE_DIR,
        '741c',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    ),
    os.path.join(
        FIXTURE_DIR,
        '741c',
        'fig.jpg'
    ),
]


def package_files(datafiles):
    pkg_files = list([str(item) for item in datafiles.listdir()])
    xml_file_path = pkg_files[0]
    files = pkg_files[1:]
    return xml_file_path, files


@pytest.yield_fixture
def functional_config(request):
    yield testing.setUp()
    testing.tearDown()


@pytest.fixture
def change_service(functional_config):
    return DatabaseService(
        InMemoryDBManager(database_name='test1'),
        InMemoryDBManager(database_name='test2')
    )


@pytest.fixture
def testapp(functional_config):
    settings = {
        'database_uri': 'http://localhost:5984',
        'couchdb.db_name': 'catalog_manager',
        'database_username': 'admin',
        'database_password': 'password',
    }
    test_app = main(settings)
    return TestApp(test_app)
