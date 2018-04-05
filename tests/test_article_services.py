import os
from unittest.mock import patch

from catalog_persistence.databases import (
    InMemoryDBManager,
    DatabaseService,
    DocumentNotFound
)
from catalog_persistence.models import (
    RecordType,
)

from catalogmanager.article_services import(
    ArticleServices,
)


def get_article(filename):
    path = os.path.dirname(filename)
    files = [path + '/' + item for item in os.listdir(path) if not item.endswith('.xml')]
    xml_filename = filename
    return (xml_filename, files)


def test_receive_article():

    xml_filename = './packages/0034-8910-rsp-S01518-87872016050006741/0034-8910-rsp-S01518-87872016050006741.xml'
    xml_filename, files = get_article(xml_filename)

    changes_db_manager = InMemoryDBManager(database_name='changes')
    articles_db_manager = InMemoryDBManager(database_name='articles')

    article_services = ArticleServices(articles_db_manager, changes_db_manager)

    article_content = {
        'xml': '0034-8910-rsp-S01518-87872016050006741.xml',
        'assets': [
            {
                'file_href': '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
                'file_id': '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
            },
            {
                'file_href': '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
                'file_id': '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg'
            },
        ]
    }

    expected = {
        'attachments': [
            '0034-8910-rsp-S01518-87872016050006741.xml',
            '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
            '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        ],
        'content': article_content,
        'document_type': 'ART',
        'document_id': 'ID',
    }

    got = article_services.receive_article('ID', xml_filename, files)
    if 'created_date' in got.keys():
        del got['created_date']
    print(expected)
    print(got)
    assert expected == got


@patch.object(DatabaseService, 'get_attachment')
def test_get_article_file_in_database(mocked_get_attachment,
                                      change_service,
                                      inmemory_article_location,
                                      article_files):
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_id = 'ID'
    article_services.get_article_file(article_id)
    mocked_get_attachment.assert_called_with(
        document_id=article_id,
        file_id=os.path.basename(article_files[0])
    )


@patch.object(DatabaseService, 'get_attachment', side_effect=DocumentNotFound)
def test_get_article_file_not_found(mocked_get_attachment,
                                    change_service,
                                    inmemory_article_location):
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_check = article_services.get_article_file('ID')
    assert article_check is None


def test_get_article_file(change_service, inmemory_article_location, xml_test):
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_check = article_services.get_article_file('ID')
    assert article_check is not None
    assert article_check.read().decode() == xml_test
