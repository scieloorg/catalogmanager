import os
import pytest
from pyramid import testing

from managers.article_manager import ArticleManager
from managers.models.file import File
from persistence.seqnum_generator import SeqNumGenerator
from persistence.databases import (
    InMemoryDBManager,
    CouchDBManager,
)
from persistence.services import (
    DatabaseService,
    ChangesService,
)


@pytest.fixture(scope="module")
def test_fixture_dir():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'test_files',
    )


def read_file(fixture_dir, dir_path, filename):
    file_path = os.path.join(fixture_dir, dir_path, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as fb:
            xml_file = File(filename, fb.read())
            return xml_file


@pytest.fixture(scope="module")
def test_packA_filenames():
    return (
        '0034-8910-rsp-S01518-87872016050006741.xml',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
    )


@pytest.fixture(scope="module")
def test_package_A(test_fixture_dir, test_packA_filenames):
    return tuple(
        read_file(test_fixture_dir, '741a', filename)
        for filename in test_packA_filenames
    )


@pytest.fixture(scope="module")
def test_packB_filenames():
    return (
        '0034-8910-rsp-S01518-87872016050006741.xml',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
    )


@pytest.fixture(scope="module")
def test_package_B(test_fixture_dir, test_packB_filenames):
    return tuple(
        read_file(test_fixture_dir, '741b', filename)
        for filename in test_packB_filenames
    )


@pytest.fixture(scope="module")
def test_packC_filenames():
    return (
        '0034-8910-rsp-S01518-87872016050006741.xml',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        'fig.jpg'
    )


@pytest.fixture(scope="module")
def test_package_C(test_fixture_dir, test_packC_filenames):
    return tuple(
        read_file(test_fixture_dir, '741c', filename)
        for filename in test_packC_filenames
    )


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
    db_host = 'http://inmemory'
    return (
        InMemoryDBManager(database_uri=db_host, database_name='articles'),
        InMemoryDBManager(database_uri=db_host, database_name='changes')
    )


@pytest.fixture
def xml_test():
    return """
    <article xmlns:xlink="http://www.w3.org/1999/xlink"
             xmlns:mml="http://www.w3.org/1998/Math/MathML"
             dtd-version="1.0"
             article-type="research-article"
             xml:lang="en">
    </article>
    """


@pytest.fixture
def seqnumber_generator(request):
    db_host = 'http://inmemory'
    s = SeqNumGenerator(
        InMemoryDBManager(database_uri=db_host, database_name='test3'),
        'CHANGE'
    )

    def fin():
        s.db_manager.drop_database()

    request.addfinalizer(fin)
    return s


@pytest.fixture
def changes_service(request, seqnumber_generator):
    db_host = 'http://inmemory'
    return ChangesService(
        InMemoryDBManager(database_uri=db_host, database_name='test2'),
        seqnumber_generator
    )


@pytest.fixture
def databaseservice_params(functional_config, changes_service):
    db_host = 'http://inmemory'
    return (
        InMemoryDBManager(database_uri=db_host, database_name='test1'),
        changes_service
    )


@pytest.fixture
def setup(request, functional_config, databaseservice_params):
    database_service = DatabaseService(
        databaseservice_params[0],
        databaseservice_params[1])

    def fin():
        database_service.db_manager.drop_database()
        database_service.changes_service.changes_db_manager.drop_database()
    request.addfinalizer(fin)


@pytest.fixture
def set_inmemory_article_manager(setup, databaseservice_params):
    db_host = 'http://inmemory'
    return ArticleManager(
        InMemoryDBManager(database_uri=db_host, database_name='articles'),
        InMemoryDBManager(database_uri=db_host, database_name='files'),
        databaseservice_params[1])


@pytest.fixture
def inmemory_receive_package(set_inmemory_article_manager, test_package_A):
    return set_inmemory_article_manager.receive_package(
        id='ID',
        xml_file=test_package_A[0],
        files=test_package_A[1:])


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
    seqnum_database_config = couchdb_config.copy()
    seqnum_database_config['database_name'] = "seqnum"

    seqnumber_generator = SeqNumGenerator(
        CouchDBManager(**seqnum_database_config),
        'CHANGE'
    )
    changes_service = ChangesService(
        CouchDBManager(**changes_database_config),
        seqnumber_generator
    )
    return (
        CouchDBManager(**articles_database_config),
        changes_service
    )


@pytest.fixture
def couchdb_receive_package(dbserver_service, test_package_A):
    article_manager = ArticleManager(
        dbserver_service[0],
        dbserver_service[1]
    )
    return article_manager.receive_package(id='ID',
                                           xml_file=test_package_A[0],
                                           files=test_package_A[1:])


@pytest.fixture
def list_changes_expected():
    return [
        {
            "change_id": "{}".format(id),
            "document_id": "ID-{}".format(id),
            "document_type": "ARTICLE",
            "type": "CREATE",
        }
        for id in range(123457, 123466)
    ]
