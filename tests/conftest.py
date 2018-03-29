import pytest
from pyramid import testing
from webtest import TestApp

from catalogmanager.article_services import ArticleServices
from catalog_persistence import main
from catalog_persistence.databases import InMemoryDBManager, DatabaseService


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
def article_location(change_service,
                     tmpdir,
                     xml_test):
    article_tmp_dir = tmpdir.mkdir("articles")
    xml_file = article_tmp_dir.join("article.xml")
    xml_file.write(xml_test)
    files = [
        article_tmp_dir.join(image).strpath
        for image in ["img1.png", "img2.png", "img3.png"]
    ]
    article_services = ArticleServices(change_service[0], change_service[1])
    return article_services.receive_article(xml_file.strpath, files)


@pytest.fixture
def database_config():
    return {
        'db_host': 'http://localhost',
        'db_port': '1234',
        'username': 'admin',
        'password': 'admin'
    }
