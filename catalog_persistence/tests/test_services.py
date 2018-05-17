

def test_list_changes_returns_db_manager_find_all(inmemory_db_setup,
                                                  test_changes_records,
                                                  xml_test):
    for change_record in test_changes_records:
        inmemory_db_setup.changes_db_manager.create(change_record['change_id'],
                                                    change_record)
    last_sequence = ''
    limit = 10
    check_list = inmemory_db_setup.list_changes(last_sequence=last_sequence,
                                                limit=limit)
    assert len(check_list) == len(test_changes_records)
    for check_item, expected_item in zip(check_list, test_changes_records):
        assert check_item['change_id'] == expected_item['change_id']
        assert check_item['document_id'] == expected_item['document_id']
        assert check_item['type'] == expected_item['type']
        assert check_item['created_date'] is not None


def test_list_changes_returns_db_manager_find_from_last(inmemory_db_setup,
                                                        test_changes_records,
                                                        xml_test):
    for change_record in test_changes_records:
        inmemory_db_setup.changes_db_manager.create(change_record['change_id'],
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
        assert check_item['type'] == expected_item['type']
        assert check_item['created_date'] is not None


def test_list_changes_returns_db_manager_find_limit(inmemory_db_setup,
                                                    test_changes_records,
                                                    xml_test):
    for change_record in test_changes_records:
        inmemory_db_setup.changes_db_manager.create(change_record['change_id'],
                                                    change_record)
    last_record = 2
    last_sequence = test_changes_records[last_record]['change_id']
    limit = 5
    check_list = inmemory_db_setup.list_changes(last_sequence=last_sequence,
                                                limit=limit)
    assert len(check_list) == len(test_changes_records[last_record + 1:])
    for check_item, expected_item in \
            zip(check_list, test_changes_records[last_record + 1:limit + 1]):
        assert check_item['change_id'] == expected_item['change_id']
        assert check_item['document_id'] == expected_item['document_id']
        assert check_item['type'] == expected_item['type']
        assert check_item['created_date'] is not None


def test_list_changes_returns_db_manager_find_no_changes(inmemory_db_setup,
                                                         test_changes_records,
                                                         xml_test):
    for change_record in test_changes_records:
        inmemory_db_setup.changes_db_manager.create(change_record['change_id'],
                                                    change_record)
    last_sequence = test_changes_records[-1]['change_id']
    limit = 5
    check_list = inmemory_db_setup.list_changes(last_sequence=last_sequence,
                                                limit=limit)
    assert len(check_list) == 0
