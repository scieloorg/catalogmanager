import os
from unittest.mock import patch

import pytest

from catalog_persistence.databases import (
    InMemoryDBManager,
    DatabaseService,
    DocumentNotFound
)
from catalog_persistence.models import RecordType
from catalogmanager.article_services import (
    ArticleServices,
    ArticleServicesException
)
from catalogmanager.models.article_model import (
    Article,
)
from catalogmanager.xml.xml_tree import (
    XMLTree
)
from .conftest import (
    PKG_A,
)


def test_receive_xml_file():

    xml_file_path, _ = PKG_A[0], PKG_A[1:]

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
    article_services.receive_xml_file('ID', xml_file_path)
    got = article_services.article_db_service.read('ID')
    assert got['content']['xml'] == expected['content']['xml']
    assert sorted(got['content'].get('assets')) == sorted(expected_assets)
    assert sorted(got['attachments']) == sorted(
        expected['attachments'])


def test_receive_package():

    xml_file_path, files = PKG_A[0], PKG_A[1:]
    article = Article('ID')
    article.xml_file = xml_file_path
    article.update_asset_files(files)

    changes_db_manager = InMemoryDBManager(database_name='changes')
    articles_db_manager = InMemoryDBManager(database_name='articles')

    article_services = ArticleServices(articles_db_manager, changes_db_manager)

    unexpected, missing = article_services.receive_package(
        'ID', xml_file_path, files)
    assert unexpected == []
    assert missing == []


@patch.object(DatabaseService, 'read')
def test_get_article_in_database(mocked_dataservices_read,
                                 setup,
                                 change_service,
                                 inmemory_receive_package):
    article_id = 'ID'
    mocked_dataservices_read.return_value = {'document_id': article_id}
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_check = article_services.get_article_data(article_id)
    assert article_check is not None
    assert isinstance(article_check, dict)
    mocked_dataservices_read.assert_called_with(article_id)


@patch.object(DatabaseService, 'read', side_effect=DocumentNotFound)
def test_get_article_in_database_not_found(mocked_dataservices_read,
                                           setup,
                                           change_service,
                                           inmemory_receive_package):
    article_id = 'ID'
    mocked_dataservices_read.return_value = {'document_id': article_id}
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    pytest.raises(
        ArticleServicesException,
        article_services.get_article_data,
        article_id
    )


def test_get_article_record(setup,
                            change_service,
                            inmemory_receive_package,
                            article_file,
                            assets_files):
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_id = 'ID'
    article_check = article_services.get_article_data(article_id)
    assert article_check is not None
    assert isinstance(article_check, dict)
    assert article_check.get('document_id') == article_id
    assert article_check.get('document_type') == RecordType.ARTICLE.value
    assert article_check.get('content') is not None
    assert isinstance(article_check['content'], dict)
    assert article_check['content'].get('xml') is not None
    assert article_check.get('created_date') is not None
    assert article_check.get('attachments') is not None
    assert isinstance(article_check['attachments'], list)


@patch.object(DatabaseService, 'get_attachment')
def test_get_article_file_in_database(mocked_get_attachment,
                                      setup,
                                      change_service,
                                      inmemory_receive_package):
    article_id = 'ID'
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_services.get_article_file(article_id)
    mocked_get_attachment.assert_called_with(
        document_id=article_id,
        file_id=os.path.basename(PKG_A[0])
    )


@patch.object(DatabaseService, 'get_attachment', side_effect=DocumentNotFound)
def test_get_article_file_not_found(mocked_get_attachment,
                                    setup,
                                    change_service,
                                    inmemory_receive_package):
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    pytest.raises(
        ArticleServicesException,
        article_services.get_article_file,
        'ID'
    )


def test_get_article_file(setup, change_service, inmemory_receive_package):
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_check = article_services.get_article_file('ID')
    assert article_check is not None
    with open(PKG_A[0], 'rb') as file:
        xml_tree = XMLTree()
        xml_tree.content = file.read()
        assert xml_tree.compare(article_check)


@patch.object(DatabaseService, 'get_attachment', side_effect=DocumentNotFound)
def test_get_asset_file_not_found(mocked_get_attachment,
                                    setup,
                                    change_service,
                                    inmemory_receive_package):
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    pytest.raises(
        ArticleServicesException,
        article_services.get_asset_file,
        'ID',
        'file_id'
    )


def test_get_asset_file():
    xml_file_path, files = PKG_A[0], PKG_A[1:]

    changes_db_manager = InMemoryDBManager(database_name='changes')
    articles_db_manager = InMemoryDBManager(database_name='articles')

    article_services = ArticleServices(articles_db_manager, changes_db_manager)
    article_services.receive_package('ID', xml_file_path, files)
    for f in files:
        name = os.path.basename(f)
        assert open(f, 'rb').read() == article_services.get_asset_file(
            'ID', name)


def test_get_asset_files():
    xml_file_path, files = PKG_A[0], PKG_A[1:]

    changes_db_manager = InMemoryDBManager(database_name='changes')
    articles_db_manager = InMemoryDBManager(database_name='articles')

    article_services = ArticleServices(articles_db_manager, changes_db_manager)
    article_services.receive_package('ID', xml_file_path, files)

    items, msg = article_services.get_asset_files('ID')
    assert len(items) == len(files)
    assert len(msg) == 0
    for f in files:
        assert open(f, 'rb').read() in items
