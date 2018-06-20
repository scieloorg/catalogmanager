from unittest.mock import patch

import pytest

from persistence.databases import DBFailed, DocumentNotFound, InMemoryDBManager
from persistence.services import DatabaseService
from managers.article_manager import (
    ArticleManager,
    ArticleManagerException
)
from managers.models.article_model import ArticleDocument
from managers.xml.xml_tree import (
    XMLTree
)


def test_receive_xml_file(set_inmemory_article_manager, test_package_A,
                          test_packA_filenames):
    article_manager = set_inmemory_article_manager
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


def test_receive_package(set_inmemory_article_manager, test_package_A):
    article_manager = set_inmemory_article_manager
    unexpected, missing = article_manager.receive_package(
        id='ID',
        xml_file=test_package_A[0],
        files=test_package_A[1:]
    )
    assert unexpected == []
    assert missing == []


def test_article_manager(databaseservice_params):
    db_host = 'http://inmemory'
    article_manager = ArticleManager(
        InMemoryDBManager(database_uri=db_host, database_name='articles'),
        InMemoryDBManager(database_uri=db_host, database_name='files'),
        databaseservice_params[1]
    )
    assert article_manager.article_db_service is not None
    assert isinstance(article_manager.article_db_service, DatabaseService)
    assert article_manager.file_db_service is not None
    assert isinstance(article_manager.file_db_service, DatabaseService)


@patch.object(DatabaseService, 'add_file', side_effect=Exception())
def test_add_document_add_file_error(mocked_register,
                                     set_inmemory_article_manager,
                                     test_package_A):
    article_document = ArticleDocument(test_package_A[0].name)
    article_manager = set_inmemory_article_manager
    pytest.raises(
        Exception,
        article_manager.add_document,
        article_document
    )


@patch.object(DatabaseService, 'register')
def test_add_document_add_file_with_file_name_and_content(
    mocked_register,
    set_inmemory_article_manager,
    test_package_A
):
    xml_file = test_package_A[0]
    article_document = ArticleDocument(xml_file.name)
    article_document.add_version(xml_file.name, xml_file.content)
    article_manager = set_inmemory_article_manager
    with patch.object(article_manager.file_db_service, 'add_file') \
            as mocked_add_file:
        article_manager.add_document(article_document)
        mocked_add_file.assert_called_once_with(
            file_id=article_document.xml_file_id,
            content=article_document.xml_tree.content
        )


@patch.object(DatabaseService, 'add_file')
@patch.object(DatabaseService, 'register')
def test_add_document_updates_article_document_xml_file_id(
    mocked_register,
    mocked_add_file,
    set_inmemory_article_manager,
    test_package_A
):
    xml_file = test_package_A[0]
    article_document = ArticleDocument(xml_file.name)
    article_document.add_version(xml_file.name, xml_file.content)
    added_file_url = '/rawfile/' + article_document.xml_file_id
    mocked_add_file.return_value = added_file_url
    article_manager = set_inmemory_article_manager
    article_manager.add_document(article_document)
    assert article_document.versions[-1]['data'] == added_file_url


def test_add_document_article_get_record(set_inmemory_article_manager,
                                         test_package_A):
    xml_file = test_package_A[0]
    article_document = ArticleDocument(xml_file.name)
    article_document.add_version(xml_file.name, xml_file.content)
    with patch.object(article_document, 'get_record'):
        article_manager = set_inmemory_article_manager
        article_manager.add_document(article_document)
        article_document.get_record.assert_called_once()


@patch.object(DatabaseService, 'register', side_effect=Exception())
def test_add_document_register_to_database_error(mocked_register,
                                                 set_inmemory_article_manager,
                                                 test_package_A):
    xml_file = test_package_A[0]
    article_document = ArticleDocument(xml_file.name)
    article_document.add_version(xml_file.name, xml_file.content)
    article_manager = set_inmemory_article_manager
    pytest.raises(
        Exception,
        article_manager.add_document,
        article_document
    )


@patch.object(DatabaseService, 'register')
def test_add_document_register_with_article_record(
    mocked_register,
    set_inmemory_article_manager,
    test_package_A
):
    xml_file = test_package_A[0]
    fake_article_record = {
        'document_id': '1234',
        'content': b'acbdet'
    }
    article_document = ArticleDocument(xml_file.name)
    article_document.add_version(xml_file.name, xml_file.content)
    article_manager = set_inmemory_article_manager
    with patch.object(article_document, 'get_record'):
        article_document.get_record.return_value = fake_article_record
        article_manager = set_inmemory_article_manager
        article_manager.add_document(article_document)
        mocked_register.assert_called_with(xml_file.name, fake_article_record)


def test_add_document_register_to_database_ok_returns_article_url(
    set_inmemory_article_manager,
    test_package_A
):
    xml_file = test_package_A[0]
    article_document = ArticleDocument('ID')
    article_document.add_version(xml_file.name, xml_file.content)
    article_manager = set_inmemory_article_manager
    article_url = article_manager.add_document(article_document)
    assert article_url is not None
    assert article_url.endswith('/' + xml_file.name)


@patch.object(DatabaseService, 'read')
def test_get_article_in_database(mocked_dataservices_read,
                                 setup,
                                 set_inmemory_article_manager,
                                 inmemory_receive_package):
    article_id = 'ID'
    mocked_dataservices_read.return_value = {'document_id': article_id}
    article_manager = set_inmemory_article_manager
    article_document = article_manager.get_article_document(article_id)
    assert article_document is not None
    assert isinstance(article_document, ArticleDocument)
    mocked_dataservices_read.assert_called_with(article_id)


@patch.object(DatabaseService, 'read', side_effect=DocumentNotFound)
def test_get_article_in_database_not_found(mocked_dataservices_read,
                                           setup,
                                           set_inmemory_article_manager,
                                           inmemory_receive_package):
    article_id = 'ID'
    mocked_dataservices_read.return_value = {'document_id': article_id}

    article_manager = set_inmemory_article_manager
    pytest.raises(
        ArticleManagerException,
        article_manager.get_article_document,
        article_id
    )


@patch.object(DatabaseService, 'read', side_effect=DBFailed)
def test_get_manifest_db_failed(mocked_dataservices_read,
                                setup,
                                set_inmemory_article_manager,
                                inmemory_receive_package):
    article_id = 'ID'
    mocked_dataservices_read.return_value = {'document_id': article_id}

    article_manager = set_inmemory_article_manager
    pytest.raises(
        DBFailed,
        article_manager.get_article_document,
        article_id
    )


def test_get_article_data(setup,
                          set_inmemory_article_manager,
                          inmemory_receive_package):
    article_manager = set_inmemory_article_manager
    article_id = 'ID'
    article_document = article_manager.get_article_document(article_id)
    assert isinstance(article_document, ArticleDocument)
    assert article_document.id == article_id
    assert isinstance(article_document.manifest, dict)


@patch.object(DatabaseService, 'get_attachment')
def test_get_article_file_in_database(mocked_get_attachment,
                                      setup,
                                      set_inmemory_article_manager,
                                      inmemory_receive_package,
                                      xml_test,
                                      test_packA_filenames):
    mocked_get_attachment.return_value = xml_test.encode('utf-8')
    article_id = 'ID'
    article_manager = set_inmemory_article_manager
    article_manager.get_article_file(article_id)
    mocked_get_attachment.assert_called_with(
        document_id=article_id,
        file_id=test_packA_filenames[0]
    )


@patch.object(DatabaseService, 'get_attachment', side_effect=DocumentNotFound)
def test_get_article_file_not_found(mocked_get_attachment,
                                    setup,
                                    set_inmemory_article_manager,
                                    inmemory_receive_package):
    article_manager = set_inmemory_article_manager
    pytest.raises(
        ArticleManagerException,
        article_manager.get_article_file,
        'ID'
    )


def test_get_article_file(setup,
                          set_inmemory_article_manager,
                          inmemory_receive_package,
                          test_package_A):
    article_manager = set_inmemory_article_manager
    article_document = article_manager.get_article_file('ID')
    assert article_document is not None
    xml_tree = XMLTree(test_package_A[0].content)
    assert xml_tree.compare(article_document)


@patch.object(DatabaseService, 'get_attachment', side_effect=DocumentNotFound)
def test_get_asset_file_not_found(mocked_get_attachment,
                                  setup,
                                  set_inmemory_article_manager,
                                  inmemory_receive_package):
    article_manager = set_inmemory_article_manager
    pytest.raises(
        ArticleManagerException,
        article_manager.get_asset_file,
        'ID',
        'file_id'
    )


def test_get_asset_file(set_inmemory_article_manager,
                        test_package_A,
                        test_packA_filenames):
    article_manager = set_inmemory_article_manager
    article_manager.receive_package(id='ID',
                                    xml_file=test_package_A[0],
                                    files=test_package_A[1:])
    for file in test_package_A[1:]:
        content_type, content = article_manager.get_asset_file(
            'ID', file.name)
        assert file.content == content


def test_get_asset_files(set_inmemory_article_manager, test_package_A):
    files = test_package_A[1:]
    article_manager = set_inmemory_article_manager
    article_manager.receive_package(id='ID',
                                    xml_file=test_package_A[0],
                                    files=test_package_A[1:])
    items, msg = article_manager.get_asset_files('ID')

    asset_contents = [
        asset_data[1]
        for name, asset_data in items.items()
        if len(asset_data) == 2
    ]
    assert len(items) == len(files)
    assert len(msg) == 0
    for asset in files:
        assert asset.content in asset_contents
