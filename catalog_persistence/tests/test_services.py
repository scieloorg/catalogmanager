from unittest.mock import Mock

from catalog_persistence.databases import QueryOperator
from catalog_persistence.services import SortOrder


def test_list_changes_returns_db_manager_find_result(setup,
                                                     database_service,
                                                     test_changes_records,
                                                     xml_test):
    expected_list = test_changes_records
    test_changes_db_manager = database_service.changes_db_manager
    database_service.changes_db_manager = Mock()
    database_service.changes_db_manager.find = Mock()
    database_service.changes_db_manager.find.return_value = expected_list
    last_sequence = 'SEQ1'
    filter_called = {
        'change_id': [
            (QueryOperator.GREATER_THAN, last_sequence)
        ]
    }
    limit = 10
    fields_called = [
        'change_id',
        'document_id',
        'document_type',
        'type',
        'created_date'
    ]
    sorted_called = [{'change_id': SortOrder.ASC.value}]
    check_list = database_service.list_changes(last_sequence='SEQ1',
                                               limit=limit)
    database_service.changes_db_manager.find.assert_called_once_with(
        fields=fields_called,
        limit=limit,
        filter=filter_called,
        sort=sorted_called
    )
    database_service.changes_db_manager = test_changes_db_manager
    assert len(check_list) == len(expected_list)
    for check_list_item, expected_item in zip(check_list, expected_list):
        assert check_list_item['document_id'] == expected_item['document_id']
        assert check_list_item['document_type'] ==\
            expected_item['document_type']
        assert check_list_item['created_date'] is not None
