#!/usr/bin/python
from datetime import datetime

import couchdb


def test_app_get_database(setup, get_database_manager):
    assert isinstance(get_database_manager._database, couchdb.client.Database)
    assert get_database_manager._db_name == get_database_manager._database.name


def test_create_document(setup, get_database_manager):
    create_date = datetime.utcnow()
    document = get_database_manager.create({
        'type': 'document',
        'create_date': create_date,
        'content': 'Test'
    })
    assert document is not None
    assert document.id is not None

    check_document = get_database_manager._database[document.id]
    assert check_document is not None
    assert check_document['type'] == 'document'
    assert check_document['content'] == 'Test'
    assert check_document['create_date'] == str(create_date.timestamp())


def test_get_document_by_id(setup, get_database_manager):
    create_date = datetime.utcnow()
    document = get_database_manager.create({
        'type': 'document',
        'create_date': create_date,
        'content': 'Test2'
    })
    assert document is not None
    assert document.id is not None

    check_document = get_database_manager.get_by_id(document.id)
    assert check_document is not None
    assert check_document['type'] == 'document'
    assert check_document['content'] == 'Test2'
    assert check_document['create_date'] == str(create_date.timestamp())
