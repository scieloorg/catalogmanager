
from pathlib import Path

import pytest
from pyramid import testing

from managers.article_manager import ArticleManager
from persistence.databases import InMemoryDBManager
from persistence.services import ChangesService
from persistence.seqnum_generator import SeqNumGenerator


@pytest.fixture
def dummy_request():
    request = testing.DummyRequest()
    request.db_settings = {
        'db_host': 'http://localhost',
        'db_port': '12345'
    }
    return request


@pytest.fixture
def inmemory_article_manager(request):
    db_host = 'http://inmemory'
    articles_dbmanager = InMemoryDBManager(database_uri=db_host,
                                           database_name='articles')
    files_dbmanager = InMemoryDBManager(database_uri=db_host,
                                        database_name='files')
    changes_dbmanager = InMemoryDBManager(database_uri=db_host,
                                          database_name='changes')
    changes_seq_dbmanager = InMemoryDBManager(database_uri=db_host,
                                              database_name='changes_seqnum')

    def fin():
        try:
            articles_dbmanager.drop_database()
            files_dbmanager.drop_database()
            changes_dbmanager.drop_database()
            changes_seq_dbmanager.drop_database()
        except Exception:
            pass

    request.addfinalizer(fin)
    return ArticleManager(
        articles_dbmanager,
        files_dbmanager,
        ChangesService(
            changes_dbmanager,
            SeqNumGenerator(
                changes_seq_dbmanager,
                'CHANGE'
            )
        )
    )


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
