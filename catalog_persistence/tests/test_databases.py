import pytest

from catalog_persistence.databases import DocumentNotFound
from catalog_persistence.models import ArticleRecord


def generate_id():
    from uuid import uuid4
    return uuid4().hex


def test_register_document(setup,
                           database_service):
    article = ArticleRecord({'content': 'Test'})
    document_id = database_service.register(article)
    assert document_id is not None
    assert isinstance(document_id, str)

    check_document = database_service.find()
    assert check_document is not None
    assert check_document[0].document_id == article.document_id
    assert check_document[0].document_type == article.document_type
    assert check_document[0].content == article.content
    assert check_document[0].created_date is not None


def test_read_document(setup, database_service):
    article = ArticleRecord({'content': 'Test2'})
    document_id = database_service.register(article)

    check_document = database_service.read(document_id)
    assert check_document is not None
    assert check_document.document_id == article.document_id
    assert check_document.document_type == article.document_type
    assert check_document.content == article.content
    assert check_document.created_date is not None


def test_read_document_not_found(setup, database_service):
    pytest.raises(DocumentNotFound, "database_service.read('idnaoexistente')")


# def test_update_document(setup, database_service):
#     article = ArticleRecord({'content': 'Test3'})
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
    article = ArticleRecord({'content': 'Test4'})
    document_id = database_service.register(article)

    check_document = database_service.read(document_id)
    database_service.delete(check_document)
    pytest.raises(DocumentNotFound, 'database_service.read(document_id)')


def test_delete_document_not_found(setup, database_service):
    article = ArticleRecord({'content': 'Test5'})
    pytest.raises(DocumentNotFound, 'database_service.delete(article)')
