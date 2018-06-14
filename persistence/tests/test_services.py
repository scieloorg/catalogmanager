from unittest.mock import Mock

from persistence.databases import QueryOperator
from persistence.services import ChangeType, SortOrder

from unittest.mock import patch

import pytest
from datetime import datetime
from uuid import uuid4

from persistence.models import get_record, RecordType
from persistence.databases import DocumentNotFound, UpdateFailure
from persistence.services import (
    ChangesService,
)


def get_article_record(content={'Test': 'Test'}):
    document_id = uuid4().hex
    return get_record(document_id=document_id,
                      document_type=RecordType.ARTICLE,
                      content=content,
                      created_date=datetime.utcnow())


def test_read_document(database_service):
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


def test_read_document_not_found(database_service):
    pytest.raises(
        DocumentNotFound,
        database_service.read,
        '336abebdd31894idnaoexistente'
    )


def test_list_changes_calls_db_manager_find(inmemory_db_setup,
                                            test_changes_records,
                                            xml_test):

    _changes_db_manager = inmemory_db_setup.changes_service.changes_db_manager
    _changes_db_manager.find = Mock()
    _changes_db_manager.find.return_value = []
    last_sequence = '123456'
    limit = 10
    expected_fields = [
        'change_id',
        'document_id',
        'document_type',
        'type',
        'created_date'
    ]
    filter = {
        'change_id': [
            (QueryOperator.GREATER_THAN, last_sequence)
        ]
    }
    sort = [{'change_id': SortOrder.ASC.value}]
    inmemory_db_setup.list_changes(last_sequence=last_sequence,
                                   limit=limit)
    _changes_db_manager.find.assert_called_once_with(
        fields=expected_fields,
        limit=limit,
        filter=filter,
        sort=sort
    )


def test_list_changes_returns_db_manager_find_all(inmemory_db_setup,
                                                  test_changes_records,
                                                  xml_test):
    _changes_db_manager = inmemory_db_setup.changes_service.changes_db_manager
    for change_record in test_changes_records:
        _changes_db_manager.create(
            change_record['change_id'],
            change_record)
    last_sequence = ''
    limit = 10
    check_list = inmemory_db_setup.list_changes(last_sequence=last_sequence,
                                                limit=limit)
    assert len(check_list) == len(test_changes_records)
    for check_item, expected_item in zip(check_list, test_changes_records):
        assert check_item['change_id'] == expected_item['change_id']
        assert check_item['document_id'] == expected_item['document_id']
        assert check_item['type'] == ChangeType(expected_item['type']).name
        assert check_item['created_date'] is not None


def test_list_changes_returns_db_manager_find_from_last(inmemory_db_setup,
                                                        test_changes_records,
                                                        xml_test):
    _changes_db_manager = inmemory_db_setup.changes_service.changes_db_manager
    for change_record in test_changes_records:
        _changes_db_manager.create(
            change_record['change_id'],
            change_record)
    last_record = 4
    last_sequence = test_changes_records[last_record]['change_id']
    limit = 10
    check_list = inmemory_db_setup.list_changes(last_sequence=last_sequence,
                                                limit=limit)
    assert len(check_list) == len(test_changes_records[last_record + 1:])
    for check_item, expected_item in \
            zip(check_list, test_changes_records[last_record + 1:]):
        assert check_item['change_id'] == expected_item['change_id']
        assert check_item['document_id'] == expected_item['document_id']
        assert check_item['type'] == ChangeType(expected_item['type']).name
        assert check_item['created_date'] is not None


def test_list_changes_returns_db_manager_find_limit(inmemory_db_setup,
                                                    test_changes_records,
                                                    xml_test):
    _changes_db_manager = inmemory_db_setup.changes_service.changes_db_manager
    for change_record in test_changes_records:
        _changes_db_manager.create(
            change_record['change_id'],
            change_record)
    last_record = 2
    last_sequence = test_changes_records[last_record]['change_id']
    limit = 5
    check_list = inmemory_db_setup.list_changes(last_sequence=last_sequence,
                                                limit=limit)
    assert len(check_list) == limit
    for check_item, expected_item in \
            zip(check_list, test_changes_records[last_record + 1:limit + 1]):
        assert check_item['change_id'] == expected_item['change_id']
        assert check_item['document_id'] == expected_item['document_id']
        assert check_item['type'] == ChangeType(expected_item['type']).name
        assert check_item['created_date'] is not None


def test_list_changes_returns_db_manager_find_no_changes(inmemory_db_setup,
                                                         test_changes_records,
                                                         xml_test):
    _changes_db_manager = inmemory_db_setup.changes_service.changes_db_manager
    for change_record in test_changes_records:
        _changes_db_manager.create(
            change_record['change_id'],
            change_record)
    last_sequence = test_changes_records[-1]['change_id']
    limit = 5
    check_list = inmemory_db_setup.list_changes(last_sequence=last_sequence,
                                                limit=limit)
    assert len(check_list) == 0


def test_delete_document(database_service):
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


@patch.object(ChangesService, 'register_change')
def test_delete_document_register_change(mocked_register_change,
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


def test_delete_document_not_found(database_service):
    article_record = get_article_record({'Test': 'Test6'})
    pytest.raises(
        DocumentNotFound,
        database_service.delete,
        article_record['document_id'],
        article_record
    )


def test_delete_document_update_failure(database_service):
    article_record = get_article_record({'Test': 'Test10'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    read = database_service.read(article_record['document_id'])
    updated = read.copy()
    database_service.update(
        article_record['document_id'], updated)

    error_msg = 'Document {} not allowed to delete'.format(
                article_record['document_id'])
    with pytest.raises(UpdateFailure, message=error_msg):
        database_service.delete(article_record['document_id'], read)
