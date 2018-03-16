import pytest

from catalog_persistence.databases import DocumentNotFound


def generate_id():
    from uuid import uuid4
    return uuid4().hex


def test_register_document(setup,
                           database_service):
    document_test = {
        '_id': generate_id(),
        'document_type': 'A',
        'content': 'Test'
    }
    document_id = database_service.register(document_test)
    assert document_id is not None
    assert isinstance(document_id, str)

    check_document = database_service.collection.database.get(document_id)
    assert check_document is not None
    assert check_document['type'] == document_test['type']
    assert check_document['content'] == document_test['content']
    converted_date = str(document_test['created_date'].timestamp())
    assert check_document['created_date'] == converted_date


def test_read_document(setup, database_service):
    document_test = {
        '_id': generate_id(),
        'document_type': 'A',
        'content': 'Test2'
    }
    document_id = database_service.register(document_test)
    assert document_id is not None
    assert isinstance(document_id, str)

    check_document = database_service.read(document_id)
    assert check_document is not None
    assert check_document['type'] == document_test['type']
    assert check_document['content'] == document_test['content']
    converted_date = str(document_test['created_date'].timestamp())
    assert check_document['created_date'] == converted_date


def test_update_document(setup, database_service):
    document_test = {
        '_id': generate_id(),
        'document_type': 'A',
        'content': 'Test3'
    }
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


def test_delete_document(setup, database_service):
    document_test = {
        '_id': generate_id(),
        'document_type': 'A',
        'content': 'Test4'
    }
    document_id = database_service.register(document_test)
    assert document_id is not None
    assert isinstance(document_id, str)

    database_service.delete(document_id)
    pytest.raises(DocumentNotFound, 'database_service.read(document_id)')


def test_find_document(setup,
                       database_service,
                       fake_change_list):
    for content in fake_change_list:
        document_test = {
            '_id': generate_id(),
            'document_type': 'A',
            'content': content
        }
        database_service.register(document_test)

    check_list = database_service.find()
    assert check_list is not None
    assert len(check_list) == len(fake_change_list)
    for document in check_list:
        assert document['content'] in fake_change_list
