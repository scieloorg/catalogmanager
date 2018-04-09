import os
import pytest
from pyramid import testing
from webtest import TestApp

from catalogmanager.article_services import ArticleServices
from catalog_persistence import main
from catalog_persistence.databases import (
    InMemoryDBManager,
    CouchDBManager,
    DatabaseService
)


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
    return (
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


@pytest.fixture
def xml_test():
    return """
    <article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:mml="http://www.w3.org/1998/Math/MathML" dtd-version="1.0" article-type="research-article" xml:lang="en">
    </article>
    """


@pytest.fixture
def article_db_settings():
    return {
        'database_uri': 'http://localhost:5984',
        'database_username': 'admin',
        'database_password': 'password',
        'database_name': 'articles',
    }


@pytest.fixture
def change_db_settings():
    return {
        'database_uri': 'http://localhost:5984',
        'database_username': 'admin',
        'database_password': 'password',
        'database_name': 'changes',
    }


@pytest.fixture
def setup(request, functional_config, change_service):
    database_service = DatabaseService(change_service[0], change_service[1])

    def fin():
        database_service.db_manager.drop_database()
        database_service.changes_db_manager.drop_database()
    request.addfinalizer(fin)


@pytest.fixture
def article_tmp_dir(tmpdir):
    return tmpdir.mkdir("articles")


@pytest.fixture
def assets_files(setup, article_tmp_dir, xml_test):
    files = []
    for image in ["img1.png", "img2.png", "img3.png"]:
        img = article_tmp_dir.join(image)
        img.write(image.encode('utf-8'))
        files.append(img.strpath)
    return files


@pytest.fixture
def article_file(setup, article_tmp_dir, xml_test):
    xml_file = article_tmp_dir.join("article.xml")
    xml_file.write(xml_test)
    return xml_file.strpath


@pytest.fixture
def inmemory_receive_article(change_service, article_file, assets_files):
    article_services = ArticleServices(change_service[0], change_service[1])
    return article_services.receive_package('ID', article_file, assets_files)


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
def couchdb_receive_article(dbserver_service, article_file, assets_files):
    article_services = ArticleServices(
        dbserver_service[0],
        dbserver_service[1]
    )
    return article_services.receive_package('ID', article_file, assets_files)
