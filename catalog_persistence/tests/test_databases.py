import pytest

from catalog_persistence.databases import DocumentNotFound


def test_couchdb_register_document(setup,
                                   database_service,
                                   get_couchdb_manager,
                                   document_test):
    document_test.update({
        'content': 'Test'
    })
    document_id = database_service.register(document_test)
    assert document_id is not None
    assert isinstance(document_id, str)

    get_couchdb_manager._database = document_test['type']
    check_document = get_couchdb_manager._database.get(document_id)
    assert check_document is not None
    assert check_document['type'] == document_test['type']
    assert check_document['content'] == document_test['content']
    converted_date = str(document_test['created_date'].timestamp())
    assert check_document['created_date'] == converted_date


def test_couchdb_read_document(setup, database_service, document_test):
    document_test.update({
        'content': 'Test2'
    })
    document_id = database_service.register(document_test)
    assert document_id is not None
    assert isinstance(document_id, str)

    check_document = database_service.read(document_id)
    assert check_document is not None
    assert check_document['type'] == document_test['type']
    assert check_document['content'] == document_test['content']
    converted_date = str(document_test['created_date'].timestamp())
    assert check_document['created_date'] == converted_date


def test_couchdb_update_document(setup, database_service, document_test):
    document_test.update({
        'content': 'Test3'
    })
    document_id = database_service.register(document_test)
    assert document_id is not None
    assert isinstance(document_id, str)

    update_document = database_service.read(document_id)
    update_document['content'] = 'Test3-updated'
    update_id = database_service.update(update_document)
    assert update_id is not None

    check_document = database_service.read(document_id)
    assert check_document is not None
    assert check_document['content'] == update_document['content']


def test_couchdb_delete_document(setup, database_service, document_test):
    document_test.update({
        'content': 'Test4'
    })
    document_id = database_service.register(document_test)
    assert document_id is not None
    assert isinstance(document_id, str)

    database_service.delete(document_id)
    pytest.raises(DocumentNotFound, 'database_service.read(document_id)')
