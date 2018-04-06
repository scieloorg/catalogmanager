
from catalog_persistence.databases import (
    InMemoryDBManager,
)

from catalogmanager.article_services import(
    ArticleServices,
)

from catalogmanager.models.article_model import(
    Article,
)

from .conftest import (
    PKG_A,
)


def test_receive_xml_file():

    xml_file_path, files = PKG_A[0], PKG_A[1:]

    changes_db_manager = InMemoryDBManager(database_name='changes')
    articles_db_manager = InMemoryDBManager(database_name='articles')

    article_services = ArticleServices(articles_db_manager, changes_db_manager)

    article_content = {
        'xml': '0034-8910-rsp-S01518-87872016050006741.xml',
    }

    expected = {
        'attachments': [
            '0034-8910-rsp-S01518-87872016050006741.xml',
        ],
        'content': article_content,
        'document_type': 'ART',
        'document_id': 'ID',
    }

    expected_assets = [
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
    ]
    article = article_services.receive_xml_file('ID', xml_file_path)
    got = article_services.article_db_service.read('ID')
    assert got['content']['xml'] == expected['content']['xml']
    assert sorted(got['content'].get('assets')) == sorted(expected_assets)
    assert sorted(got['attachments']) == sorted(
        expected['attachments'])


def test_receive_package():

    xml_file_path, files = PKG_A[0], PKG_A[1:]
    article = Article('ID')
    article.xml_file = xml_file_path
    assets = article.update_asset_files(files)

    changes_db_manager = InMemoryDBManager(database_name='changes')
    articles_db_manager = InMemoryDBManager(database_name='articles')

    article_services = ArticleServices(articles_db_manager, changes_db_manager)

    unexpected, missing = article_services.receive_package(
        'ID', xml_file_path, files)
    assert unexpected == []
    assert missing == []
