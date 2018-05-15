
from pathlib import Path

import couchdb
import pytest
from pyramid.paster import get_appsettings
from webtest import TestApp

from catalogmanager_api import main


@pytest.fixture
def db_settings():
    #XXX apenas a implementação in-memory deveria ser usada como dependência
    #dos testes.  A instância real do CouchDB nunca deveria ser contactada.
    ini_settings = get_appsettings('development.ini')
    return {
        'database_uri': '{}:{}'.format(
            ini_settings['catalogmanager.db.host'],
            ini_settings['catalogmanager.db.port']
        ),
        'database_username': ini_settings['catalogmanager.db.username'],
        'database_password': ini_settings['catalogmanager.db.password']
    }


@pytest.fixture
def testapp(request, db_settings):
    settings = {'__file__': 'development.ini'}
    test_app = main(settings)

    def drop_database():
        db_server = couchdb.Server(db_settings['database_uri'])
        db_server.resource.credentials = (db_settings['database_username'],
                                          db_settings['database_password'])
        try:
            db_server.delete('changes')
            db_server.delete('articles')
        except couchdb.http.ResourceNotFound:
            pass
    request.addfinalizer(drop_database)
    return TestApp(test_app)


@pytest.fixture
def test_xml_file():
    return """
    <article article-type="research-article"
             dtd-version="1.0"
             specific-use="sps-1.2"
             xml:lang="en"
             xmlns:mml="http://www.w3.org/1998/Math/MathML"
             xmlns:xlink="http://www.w3.org/1999/xlink">
        <graphic xlink:href="0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg"/>
        <graphic xlink:href="0034-8910-rsp-S01518-87872016050006741-gf01.jpg"/>
    </article>
    """


@pytest.fixture
def test_assets_filenames():
    return (
        '0034-8910-rsp-S01518-87872016050006741.xml',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    )


@pytest.fixture
def test_article_files(test_assets_filenames):
    fixture_dir = Path(str(Path(__file__).parent)) / 'test_files' / '741a'
    return tuple(
        fixture_dir.joinpath(filename).absolute()
        for filename in test_assets_filenames
    )
