from catalog_persistence.databases import ChangeType
from catalog_persistence.models import ArticleRecord


def generate_id():
    from uuid import uuid4
    return uuid4().hex


def test_register_create_change(setup, database_service):
    article = ArticleRecord({'content': 'ChangeRecord'})
    change_id = database_service._register_change(article, ChangeType.CREATE)

    database_service.db_manager.database, document_database = (
        database_service.changes_database,
        database_service.db_manager.database_name
    )
    check_change = dict(database_service.db_manager.database[change_id])
    database_service.db_manager.database = document_database
    assert check_change is not None
    assert check_change['document_id'] == article.document_id
    assert check_change['document_type'] == article.document_type.value
    assert check_change['type'] == ChangeType.CREATE.value
    assert check_change['created_date'] is not None


def test_register_update_change(setup, database_service):
    article = ArticleRecord({'content': 'ChangeRecord2'})
    change_id = database_service._register_change(article, ChangeType.UPDATE)

    database_service.db_manager.database, document_database = (
        database_service.changes_database,
        database_service.db_manager.database_name
    )
    check_change = dict(database_service.db_manager.database[change_id])
    database_service.db_manager.database = document_database
    assert check_change is not None
    assert check_change['document_id'] == article.document_id
    assert check_change['document_type'] == article.document_type.value
    assert check_change['type'] == ChangeType.UPDATE.value
    assert check_change['created_date'] is not None


def test_register_delete_change(setup, database_service):
    article = ArticleRecord({'content': 'ChangeRecord3'})
    change_id = database_service._register_change(article, ChangeType.DELETE)

    database_service.db_manager.database, document_database = (
        database_service.changes_database,
        database_service.db_manager.database_name
    )
    check_change = dict(database_service.db_manager.database[change_id])
    database_service.db_manager.database = document_database
    assert check_change is not None
    assert check_change['document_id'] == article.document_id
    assert check_change['document_type'] == article.document_type.value
    assert check_change['type'] == ChangeType.DELETE.value
    assert check_change['created_date'] is not None
