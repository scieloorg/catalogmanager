from unittest.mock import patch

import pytest

from persistence.databases import (
    DocumentNotFound,
    DBFailed,
)
from persistence.services import DatabaseService
from persistence.models import RecordType

from managers.models.article_model import (
    ArticleDocument,
)
from managers.article_manager import (
    ArticleManager,
    ArticleManagerException
)
from managers.xml.xml_tree import (
    XMLTree
)


def test_receive_xml_file(databaseservice_params, test_package_A,
                          test_packA_filenames):
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1])
    expected = {
        'attachments': [test_packA_filenames[0]],
        'content': {
            'xml': test_packA_filenames[0],
        },
        'document_type': 'ART',
        'document_id': 'ID',
    }

    expected_assets = test_packA_filenames[1:]
    article_manager.receive_xml_file(id='ID',
                                     xml_file=test_package_A[0])
    got = article_manager.article_db_service.read('ID')
    assert got['content']['xml'] == expected['content']['xml']
    assert sorted(got['content'].get('assets')) == sorted(expected_assets)
    assert sorted(got['attachments']) == sorted(expected['attachments'])


def test_receive_package(databaseservice_params, test_package_A):
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1])
    unexpected, missing = article_manager.receive_package(
        id='ID',
        xml_file=test_package_A[0],
        files=test_package_A[1:]
    )
    assert unexpected == []
    assert missing == []


@patch.object(DatabaseService, 'read')
def test_get_article_in_database(mocked_dataservices_read,
                                 setup,
                                 databaseservice_params,
                                 inmemory_receive_package):
    article_id = 'ID'
    mocked_dataservices_read.return_value = {'document_id': article_id}
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1]
    )
    article_document = article_manager.get_article_document(article_id)
    assert isinstance(article_document, ArticleDocument)
    mocked_dataservices_read.assert_called_with(article_id)


@patch.object(DatabaseService, 'read', side_effect=DocumentNotFound)
def test_get_article_in_database_not_found(mocked_dataservices_read,
                                           setup,
                                           databaseservice_params,
                                           inmemory_receive_package):
    article_id = 'ID'
    mocked_dataservices_read.return_value = {'document_id': article_id}

    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1]
    )
    pytest.raises(
        ArticleManagerException,
        article_manager.get_article_document,
        article_id
    )


@patch.object(DatabaseService, 'read', side_effect=DBFailed)
def test_get_manifest_db_failed(mocked_dataservices_read,
                                setup,
                                databaseservice_params,
                                inmemory_receive_package):
    article_id = 'ID'
    mocked_dataservices_read.return_value = {'document_id': article_id}

    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1]
    )
    pytest.raises(
        DBFailed,
        article_manager.get_article_document,
        article_id
    )


def test_get_article_data(setup,
                          databaseservice_params,
                          inmemory_receive_package):
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1]
    )
    article_id = 'ID'
    article_document = article_manager.get_article_document(article_id)
    assert isinstance(article_document, ArticleDocument)
    assert article_document.id == article_id
    assert isinstance(article_document.manifest, dict)


@patch.object(DatabaseService, 'get_attachment')
def test_get_article_file_in_database(mocked_get_attachment,
                                      setup,
                                      databaseservice_params,
                                      inmemory_receive_package,
                                      xml_test,
                                      test_packA_filenames):
    mocked_get_attachment.return_value = xml_test.encode('utf-8')
    article_id = 'ID'
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1]
    )
    article_manager.get_article_file(article_id)
    mocked_get_attachment.assert_called_with(
        document_id=article_id,
        file_id=test_packA_filenames[0]
    )


@patch.object(DatabaseService, 'get_attachment', side_effect=DocumentNotFound)
def test_get_article_file_not_found(mocked_get_attachment,
                                    setup,
                                    databaseservice_params,
                                    inmemory_receive_package):
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1]
    )
    pytest.raises(
        ArticleManagerException,
        article_manager.get_article_file,
        'ID'
    )


def test_get_article_file(setup,
                          databaseservice_params,
                          inmemory_receive_package,
                          test_package_A):
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1]
    )
    article_document = article_manager.get_article_file('ID')
    assert article_document is not None
    xml_tree = XMLTree(test_package_A[0].content)
    assert xml_tree.compare(article_document)


@patch.object(DatabaseService, 'get_attachment', side_effect=DocumentNotFound)
def test_get_asset_file_not_found(mocked_get_attachment,
                                  setup,
                                  databaseservice_params,
                                  inmemory_receive_package):
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1]
    )
    pytest.raises(
        ArticleManagerException,
        article_manager.get_asset_file,
        'ID',
        'file_id'
    )


def test_get_asset_file(databaseservice_params,
                        test_package_A,
                        test_packA_filenames):
    article_manager = ArticleManager(
        databaseservice_params[0],
        databaseservice_params[1])
    article_manager.receive_package(id='ID',
                                    xml_file=test_package_A[0],
                                    files=test_package_A[1:])
    for file in test_package_A[1:]:
        content_type, content = article_manager.get_asset_file(
            'ID', file.name)
        assert file.content == content

