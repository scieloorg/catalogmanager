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


@pytest.yield_fixture
def functional_config(request):
    yield testing.setUp()
    testing.tearDown()


@pytest.fixture
def change_service(functional_config):
    return (
        InMemoryDBManager({'database_name': 'articles'}),
        InMemoryDBManager({'database_name': 'changes'})
    )


@pytest.fixture
def testapp(functional_config):
    settings = {
        'couchdb.uri': 'http://localhost:5984',
        'couchdb.db_name': 'catalog_manager',
        'couchdb.username': 'admin',
        'couchdb.password': 'password',
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
def article_files(tmpdir, xml_test):
    article_tmp_dir = tmpdir.mkdir("articles")
    xml_file = article_tmp_dir.join("article.xml")
    xml_file.write(xml_test)
    files = []
    for image in ["img1.png", "img2.png", "img3.png"]:
        img = article_tmp_dir.join(image)
        img.write(bytes(image, encoding='utf-8'))
        files.append(img.strpath)
    return xml_file.strpath, files


@pytest.fixture
def inmemory_article_location(change_service, article_files):
    article_services = ArticleServices(change_service[0], change_service[1])
    return article_services.receive_article(article_files[0], article_files[1])


@pytest.fixture
def database_config():
    return {
        'db_host': 'http://localhost',
        'db_port': '5984',
        'username': 'admin',
        'password': 'password'
    }


@pytest.fixture
def dbserver_service(functional_config, database_config):
    articles_database_config = database_config.copy()
    articles_database_config['database_name'] = "articles"
    changes_database_config = database_config.copy()
    changes_database_config['database_name'] = "changes"
    return (
        CouchDBManager(articles_database_config),
        CouchDBManager(changes_database_config)
    )


@pytest.fixture
def couchdb_article_location(dbserver_service, article_files):
    article_services = ArticleServices(dbserver_service[0], dbserver_service[1])
    return article_services.receive_article(article_files[0], article_files[1])
