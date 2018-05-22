from unittest.mock import patch

import pytest

from catalog_persistence.databases import DocumentNotFound
from catalog_persistence.services import DatabaseService
from catalog_persistence.models import RecordType
from catalogmanager.services import (
    ArticleServices,
    ArticleServicesException,
    ChangeService
)
from catalogmanager.xml.xml_tree import (
    XMLTree
)


def test_receive_xml_file(change_service, test_package_A,
                          test_packA_filenames):
    article_services = ArticleServices(change_service[0], change_service[1])
    expected = {
        'attachments': [test_packA_filenames[0]],
        'content': {
            'xml': test_packA_filenames[0],
        },
        'document_type': 'ART',
        'document_id': 'ID',
    }

    expected_assets = test_packA_filenames[1:]
    article_services.receive_xml_file(id='ID',
                                      xml_file=test_package_A[0])
    got = article_services.article_db_service.read('ID')
    assert got['content']['xml'] == expected['content']['xml']
    assert sorted(got['content'].get('assets')) == sorted(expected_assets)
    assert sorted(got['attachments']) == sorted(expected['attachments'])


def test_receive_package(change_service, test_package_A):
    article_services = ArticleServices(change_service[0], change_service[1])
    unexpected, missing = article_services.receive_package(
        id='ID',
        xml_file=test_package_A[0],
        files=test_package_A[1:]
    )
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
                            inmemory_receive_package):
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
                                      inmemory_receive_package,
                                      xml_test,
                                      test_packA_filenames):
    mocked_get_attachment.return_value = xml_test.encode('utf-8')
    article_id = 'ID'
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_services.get_article_file(article_id)
    mocked_get_attachment.assert_called_with(
        document_id=article_id,
        file_id=test_packA_filenames[0]
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


def test_get_article_file(setup,
                          change_service,
                          inmemory_receive_package,
                          test_package_A):
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_check = article_services.get_article_file('ID')
    assert article_check is not None
    xml_tree = XMLTree()
    xml_tree.content = test_package_A[0].content
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


def test_get_asset_file(change_service, test_package_A, test_packA_filenames):
    article_services = ArticleServices(change_service[0], change_service[1])
    article_services.receive_package(id='ID',
                                     xml_file=test_package_A[0],
                                     files=test_package_A[1:])
    for file in test_package_A[1:]:
        content_type, content = article_services.get_asset_file(
            'ID', file.name)
        assert file.content == content


def test_get_asset_files(change_service, test_package_A):
    files = test_package_A[1:]
    article_services = ArticleServices(change_service[0], change_service[1])
    article_services.receive_package(id='ID',
                                     xml_file=test_package_A[0],
                                     files=test_package_A[1:])
    items, msg = article_services.get_asset_files('ID')
    asset_contents = [
        asset_data[1]
        for name, asset_data in items.items()
        if len(asset_data) == 2
    ]
    assert len(items) == len(files)
    assert len(msg) == 0
    for asset in files:
        assert asset.content in asset_contents


@patch.object(DatabaseService, 'list_changes')
def test_list_changes_returns_changes_from_database_service(
    mocked_list_changes,
    change_service,
    list_changes_expected
):
    mocked_list_changes.return_value = list_changes_expected
    change_services = ChangeService(change_service[1])
    changes = change_services.list_changes('1', 10)
    mocked_list_changes.assert_called_once_with(last_sequence='1',
                                                limit=10)
    assert changes == list_changes_expected
