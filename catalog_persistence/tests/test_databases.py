import pytest

from catalog_persistence.databases import DocumentNotFound
from catalog_persistence.models import Record, RecordType


def test_register_document(setup, database_service):
    article = Record(
        content={'Test': 'Test1'},
        document_type=RecordType.ARTICLE
    )
    document_id = database_service.register(
        article.document_id,
        article.serialize()
    )
    assert document_id is not None
    assert isinstance(document_id, str)

    check_list = database_service.find()
    assert isinstance(check_list[0], dict)
    article_check = Record(document_id=document_id).deserialize(check_list[0])
    assert article_check.document_id == article.document_id
    assert article_check.document_type == article.document_type
    assert article_check.content == article.content
    assert article_check.created_date is not None


def test_read_document(setup, database_service):
    article = Record(
        content={'Test': 'Test2'},
        document_type=RecordType.ARTICLE
    )
    document_id = database_service.register(
        article.document_id,
        article.serialize()
    )

    record = database_service.read(document_id)
    assert record is not None
    article_check = Record(document_id=document_id).deserialize(record)
    assert article_check.document_id == article.document_id
    assert article_check.document_type == article.document_type
    assert article_check.content == article.content
    assert article_check.created_date is not None


def test_read_document_not_found(setup, database_service):
    pytest.raises(
        DocumentNotFound,
        database_service.read,
        '336abebdd31894idnaoexistente'
    )


def test_update_document(setup, database_service):
    article = Record(
        content={'Test': 'Test3'},
        document_type=RecordType.ARTICLE
    )
    document_id = database_service.register(
        article.document_id,
        article.serialize()
    )

    record = database_service.read(document_id)
    article_update = Record(document_id=document_id).deserialize(record)
    article_update.content = {'Test': 'Test3-updated'}
    update_id = database_service.update(
        document_id,
        article_update.serialize()
    )
    assert update_id is not None

    record = database_service.read(update_id)
    assert record is not None
    article_check = Record(document_id=update_id).deserialize(record)
    assert article_check.document_id == article_update.document_id
    assert article_check.document_type == article_update.document_type
    assert article_check.content == article_update.content
    assert article_check.created_date is not None
    assert article_check.updated_date is not None


def test_delete_document(setup, database_service):
    article = Record(
        content={'Test': 'Test4'},
        document_type=RecordType.ARTICLE
    )
    document_id = database_service.register(
        article.document_id,
        article.serialize()
    )

    check_document = database_service.read(document_id)
    deleted_article = Record().deserialize(check_document)
    database_service.delete(
        deleted_article.document_id,
        check_document
    )
    pytest.raises(DocumentNotFound, 'database_service.read(document_id)')


def test_delete_document_not_found(setup, database_service):
    article_record = {
        'document_id': '336abebdd31894idnaoexistente',
        'document_type': RecordType.ARTICLE.value,
        'content': {'Test': 'Test4'},
        'created_date': '01010101'
    }
    pytest.raises(
        DocumentNotFound,
        database_service.delete,
        '336abebdd31894idnaoexistente',
        article_record
    )
