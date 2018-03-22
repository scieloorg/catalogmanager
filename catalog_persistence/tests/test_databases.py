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
    article_check = Record().deserialize(check_list[0])
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

    document = database_service.read(document_id)
    assert document is not None
    article_check = Record().deserialize(document)
    assert article_check.document_id == article.document_id
    assert article_check.document_type == article.document_type
    assert article_check.content == article.content
    assert article_check.created_date is not None


def test_read_document_not_found(setup, database_service):
    pytest.raises(DocumentNotFound, "database_service.read('idnaoexistente')")


# def test_update_document(setup, database_service):
#     article = Record({'content': 'Test3'})
#     document_id = database_service.register(article)
#     assert document_id is not None
#     assert isinstance(document_id, str)
#
#     update_document = database_service.read(document_id)
#     update_document.content = 'Test3-updated'
#     update_id = database_service.update(update_document)
#     assert update_id is not None
#
#     check_document = database_service.read(document_id)
#     assert check_document is not None
#     assert check_document.content == update_document.content
#
#
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
        'document_id': '336abebdd318942101f99930da28ada5',
        'document_type': RecordType.ARTICLE.value,
        'content': 'Test5',
        'created_date': '01010101'
    }
    pytest.raises(
        DocumentNotFound,
        "database_service.delete('336abebdd318942101f99930da28ada5', article_record)"
    )
