from datetime import datetime

from catalog_persistence.databases import ChangeType
from catalog_persistence.models import ArticleRecord


def generate_id():
    from uuid import uuid4
    return uuid4().hex


def test_register_create_change(setup, database_service):
    article_record = ArticleRecord('ChangeRecord').serialize()
    article_record.update({'created_date': str(datetime.utcnow().timestamp())})
    change_id = database_service._register_change(
        article_record,
        ChangeType.CREATE
    )

    check_change = dict(database_service.changes_db_manager.database[change_id])
    assert check_change is not None
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.CREATE.value
    assert check_change['created_date'] is not None


def test_register_update_change(setup, database_service):
    article_record = ArticleRecord('ChangeRecord2').serialize()
    article_record.update({'created_date': str(datetime.utcnow().timestamp())})
    change_id = database_service._register_change(
        article_record,
        ChangeType.UPDATE
    )

    check_change = dict(database_service.changes_db_manager.database[change_id])
    assert check_change is not None
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.UPDATE.value
    assert check_change['created_date'] is not None


def test_register_delete_change(setup, database_service):
    article_record = ArticleRecord('ChangeRecord3').serialize()
    article_record.update({'created_date': str(datetime.utcnow().timestamp())})
    change_id = database_service._register_change(
        article_record,
        ChangeType.DELETE
    )

    check_change = dict(database_service.changes_db_manager.database[change_id])
    assert check_change is not None
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.DELETE.value
    assert check_change['created_date'] is not None
