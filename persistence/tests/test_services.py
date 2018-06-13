from unittest.mock import patch

from persistence.databases import QueryOperator
from persistence.services import ChangeType, SortOrder


def test_list_changes_calls_db_manager_find(inmemory_db_setup,
                                            test_changes_records,
                                            xml_test):

    _changes_db_manager = inmemory_db_setup.changes_service.changes_db_manager
    with patch.object(_changes_db_manager, 'find'):
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
