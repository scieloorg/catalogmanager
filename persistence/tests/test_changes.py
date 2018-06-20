from datetime import datetime
from random import randint
from uuid import uuid4

from persistence.services import ChangeType, SortOrder
from persistence.models import get_record, RecordType


def get_article_record(content={'Test': 'ChangeRecord'}):
    document_id = uuid4().hex
    return get_record(document_id=document_id,
                      document_type=RecordType.ARTICLE,
                      content=content,
                      created_date=datetime.utcnow())


def test_register_change_create(database_service):
    article_record = get_article_record()
    change_id = database_service.changes_service.register_change(
        article_record,
        ChangeType.CREATE
    )

    check_change = dict(
        database_service.changes_service.changes_db_manager.database[change_id]
    )
    assert check_change is not None
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.CREATE.value
    assert check_change['created_date'] is not None


def test_register_change(database_service):
    document_id = 'ID-1234'
    change_id = database_service.changes_service.register(
        document_id,
        ChangeType.CREATE
    )
    assert change_id is not None
    check_change = dict(
        database_service.changes_service.changes_db_manager.database[
            str(change_id)
        ]
    )
    assert check_change is not None
    assert check_change['document_id'] == document_id
    assert check_change['type'] == ChangeType.CREATE.value
    assert check_change['created_date'] is not None


def test_register_change_must_keep_sequential_order(database_service):
    changes_service = database_service.changes_service
    change_type_list = list(ChangeType)

    for counter in range(1, 11):
        changes_service.register(
            'ID-{}'.format(counter),
            change_type_list[randint(0, len(change_type_list)-1)]
        )
    sort = [{'change_id': SortOrder.ASC.value}]
    changes_list = changes_service.changes_db_manager.find(fields=[],
                                                           filter={},
                                                           sort=sort)

    assert changes_list is not None
    assert len(changes_list) == 10
    assert all([
        isinstance(change_list['change_id'], int)
        for change_list in changes_list
    ])
    # XXX: Usar sorted(list) ao invés de gerar uma lista ordenada
    assert all([
        changes_list[i]['change_id'] < changes_list[i + 1]['change_id']
        for i in range(len(changes_list) - 1)
    ])


def test_register_update_change(database_service):
    article_record = get_article_record({'Test': 'ChangeRecord2'})
    change_id = database_service.changes_service.register_change(
        article_record,
        ChangeType.UPDATE
    )

    check_change = dict(
        database_service.changes_service.changes_db_manager.database[change_id]
    )
    assert check_change is not None
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.UPDATE.value
    assert check_change['created_date'] is not None


def test_register_delete_change(database_service):
    article_record = get_article_record({'Test': 'ChangeRecord3'})
    change_id = database_service.changes_service.register_change(
        article_record,
        ChangeType.DELETE
    )

    check_change = dict(
        database_service.changes_service.changes_db_manager.database[change_id]
    )
    assert check_change is not None
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.DELETE.value
    assert check_change['created_date'] is not None


def test_add_attachment_create_change(database_service, xml_test):
    article_record = get_article_record({'Test': 'ChangeRecord4'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    attachment_id = "filename"
    database_service.put_attachment(
        document_id=article_record['document_id'],
        file_id=attachment_id,
        content=xml_test.encode('utf-8'),
        file_properties={
            'content_type': "text/xml",
            'content_size': len(xml_test)
        }
    )
    change_id = database_service.changes_service.register_change(
        article_record,
        ChangeType.CREATE,
        attachment_id
    )

    check_change = dict(
        database_service.changes_service.changes_db_manager.database[change_id]
    )
    assert check_change is not None
    assert check_change['attachment_id'] == attachment_id
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.CREATE.value
    assert check_change['created_date'] is not None


def test_update_attachment_create_change(database_service, xml_test):
    article_record = get_article_record({'Test': 'ChangeRecord5'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    attachment_id = "filename"
    database_service.put_attachment(
        document_id=article_record['document_id'],
        file_id=attachment_id,
        content=xml_test.encode('utf-8'),
        file_properties={
            'content_type': "text/xml",
            'content_size': len(xml_test)
        }
    )
    change_id = database_service.changes_service.register_change(
        article_record,
        ChangeType.UPDATE,
        attachment_id
    )

    check_change = dict(
        database_service.changes_service.changes_db_manager.database[change_id]
    )
    assert check_change is not None
    assert check_change['attachment_id'] == attachment_id
    assert check_change['document_id'] == article_record['document_id']
    assert check_change['document_type'] == article_record['document_type']
    assert check_change['type'] == ChangeType.UPDATE.value
    assert check_change['created_date'] is not None
