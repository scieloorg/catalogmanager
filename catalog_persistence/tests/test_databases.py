import io
from unittest.mock import patch

import pytest
from datetime import datetime
from uuid import uuid4

from catalog_persistence.databases import (
    DocumentNotFound,
    ChangeType,
    DatabaseService
)
from catalog_persistence.models import get_record, RecordType


def get_article_record(content={'Test': 'Test'}):
    document_id = uuid4().hex
    return get_record(document_id=document_id,
                      document_type=RecordType.ARTICLE,
                      content=content,
                      created_date=datetime.utcnow())


def test_register_document(setup, database_service):
    article_record = get_article_record()
    database_service.register(
        article_record['document_id'],
        article_record
    )

    check_list = database_service.find()
    assert isinstance(check_list[0], dict)
    article_check = check_list[0]
    assert article_check['document_id'] == article_record['document_id']
    assert article_check['document_type'] == article_record['document_type']
    assert article_check['content'] == article_record['content']
    assert article_check['created_date'] is not None


@patch.object(DatabaseService, '_register_change')
def test_register_document_register_change(mocked_register_change,
                                           setup,
                                           database_service):
    article_record = get_article_record()
    database_service.register(
        article_record['document_id'],
        article_record
    )

    mocked_register_change.assert_called_with(article_record,
                                              ChangeType.CREATE)


def test_read_document(setup, database_service):
    article_record = get_article_record({'Test': 'Test2'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    record_check = database_service.read(article_record['document_id'])
    assert record_check is not None
    assert record_check['document_id'] == article_record['document_id']
    assert record_check['document_type'] == article_record['document_type']
    assert record_check['content'] == article_record['content']
    assert record_check['created_date'] is not None


def test_read_document_not_found(setup, database_service):
    pytest.raises(
        DocumentNotFound,
        database_service.read,
        '336abebdd31894idnaoexistente'
    )


def test_update_document(setup, database_service):
    article_record = get_article_record({'Test': 'Test3'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    article_update = database_service.read(article_record['document_id'])
    article_update['content'] = {'Test': 'Test3-updated'}
    database_service.update(
        article_record['document_id'],
        article_update
    )

    record_check = database_service.read(article_record['document_id'])
    assert record_check is not None
    assert record_check['document_id'] == article_update['document_id']
    assert record_check['document_type'] == article_update['document_type']
    assert record_check['content'] == article_update['content']
    assert record_check['created_date'] is not None
    assert record_check['updated_date'] is not None


@patch.object(DatabaseService, '_register_change')
def test_update_document_register_change(mocked_register_change,
                                         setup,
                                         database_service):
    article_record = get_article_record({'Test': 'Test3'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    article_update = database_service.read(article_record['document_id'])
    article_update['content'] = {'Test': 'Test3-updated'}
    database_service.update(
        article_record['document_id'],
        article_update
    )

    mocked_register_change.assert_called_with(article_update,
                                              ChangeType.UPDATE)


def test_update_document_not_found(setup, database_service):
    article_record = get_article_record({'Test': 'Test4'})
    pytest.raises(
        DocumentNotFound,
        database_service.delete,
        article_record['document_id'],
        article_record
    )


def test_delete_document(setup, database_service):
    article_record = get_article_record({'Test': 'Test5'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    record_check = database_service.read(article_record['document_id'])
    database_service.delete(
        article_record['document_id'],
        record_check
    )
    pytest.raises(DocumentNotFound,
                  database_service.read,
                  article_record['document_id'])


@patch.object(DatabaseService, '_register_change')
def test_delete_document_register_change(mocked_register_change,
                                         setup,
                                         database_service):
    article_record = get_article_record({'Test': 'Test5'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    record_check = database_service.read(article_record['document_id'])
    database_service.delete(
        article_record['document_id'],
        record_check
    )

    mocked_register_change.assert_called_with(record_check,
                                              ChangeType.DELETE)


def test_delete_document_not_found(setup, database_service):
    article_record = get_article_record({'Test': 'Test6'})
    pytest.raises(
        DocumentNotFound,
        database_service.delete,
        article_record['document_id'],
        article_record
    )


def test_put_attachment_to_document(setup, database_service, xml_test):
    article_record = get_article_record({'Test': 'Test7'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    database_service.put_attachment(
        article_record['document_id'],
        "filename",
        io.StringIO(xml_test)
    )

    record_check = dict(
        database_service.db_manager.database[article_record['document_id']]
    )
    assert record_check is not None
    assert database_service.db_manager.attachment_exists(
        article_record['document_id'],
        "filename"
    )


@patch.object(DatabaseService, '_register_change')
def test_put_attachment_to_document_register_change(mocked_register_change,
                                                    setup,
                                                    database_service,
                                                    xml_test):
    article_record = get_article_record({'Test': 'Test7'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    record = database_service.read(article_record['document_id'])
    document_record = {
        'document_id': record['document_id'],
        'document_type': record['document_type'],
        'created_date': record['created_date'],
    }
    attachment_id = "filename"
    database_service.put_attachment(
        article_record['document_id'],
        attachment_id,
        io.StringIO(xml_test)
    )

    mocked_register_change.assert_called_with(document_record,
                                              ChangeType.CREATE,
                                              attachment_id)


def test_put_attachment_to_document_not_found(setup,
                                              database_service,
                                              xml_test):
    article_record = get_article_record({'Test': 'Test8'})
    pytest.raises(
        DocumentNotFound,
        database_service.put_attachment,
        article_record['document_id'],
        "filename",
        io.StringIO(xml_test)
    )


@patch.object(DatabaseService, '_register_change')
def test_update_attachment_register_change_if_it_exists(mocked_register_change,
                                                        setup,
                                                        database_service,
                                                        xml_test):
    article_record = get_article_record({'Test': 'Test9'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    attachment_id = "filename"
    database_service.put_attachment(
        article_record['document_id'],
        attachment_id,
        io.StringIO(xml_test)
    )
    record = database_service.read(article_record['document_id'])
    document_record = {
        'document_id': record['document_id'],
        'document_type': record['document_type'],
        'created_date': record['created_date'],
    }
    database_service.put_attachment(
        article_record['document_id'],
        attachment_id,
        io.StringIO(xml_test)
    )

    record_check = dict(
        database_service.db_manager.database[article_record['document_id']]
    )
    assert record_check is not None
    assert database_service.db_manager.attachment_exists(
        article_record['document_id'],
        attachment_id
    )
    mocked_register_change.assert_called_with(document_record,
                                              ChangeType.UPDATE,
                                              attachment_id)
