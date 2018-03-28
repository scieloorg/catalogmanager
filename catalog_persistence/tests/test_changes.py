import io
from datetime import datetime
from uuid import uuid4

from catalog_persistence.databases import ChangeType
from catalog_persistence.models import get_record, RecordType


def get_article_record(content={'Test': 'ChangeRecord'}):
    document_id = uuid4().hex
    return get_record(document_id=document_id,
                      document_type=RecordType.ARTICLE,
                      content=content,
                      created_date=datetime.utcnow())


def test_register_create_change(setup, database_service):
    article_record = get_article_record()
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
    article_record = get_article_record({'Test': 'ChangeRecord2'})
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
    article_record = get_article_record({'Test': 'ChangeRecord3'})
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


def test_add_attachment_create_change(setup, database_service, xml_test):
    article_record = get_article_record({'Test': 'ChangeRecord4'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    attachment_id = "filename"
    database_service.put_attachment(
        document_id=article_record['document_id'],
        file_id=attachment_id,
        content=io.StringIO(xml_test),
        content_type="text/xml",
        content_size=len(xml_test)
    )
    change_id = database_service._register_change(
        article_record,
        ChangeType.CREATE,
        attachment_id
    )

    check_change = dict(database_service.changes_db_manager.database[change_id])
    assert check_change is not None
    assert check_change['attachment_id'] == attachment_id
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.CREATE.value
    assert check_change['created_date'] is not None


def test_update_attachment_create_change(setup, database_service, xml_test):
    article_record = get_article_record({'Test': 'ChangeRecord5'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    attachment_id = "filename"
    database_service.put_attachment(
        document_id=article_record['document_id'],
        file_id=attachment_id,
        content=io.StringIO(xml_test),
        content_type="text/xml",
        content_size=len(xml_test)
    )
    change_id = database_service._register_change(
        article_record,
        ChangeType.UPDATE,
        attachment_id
    )

    check_change = dict(database_service.changes_db_manager.database[change_id])
    assert check_change is not None
    assert check_change['attachment_id'] == attachment_id
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.UPDATE.value
    assert check_change['created_date'] is not None
