from unittest.mock import patch

import pytest
from datetime import datetime
from uuid import uuid4

from persistence.databases import (
    DocumentNotFound,
    sort_results,
    DBFailed,
    CouchDBManager,
)
from persistence.services import (
    ChangesService,
    ChangeType)
from persistence.models import get_record, RecordType


def get_article_record(content={'Test': 'Test'}):
    document_id = uuid4().hex
    return get_record(document_id=document_id,
                      document_type=RecordType.ARTICLE,
                      content=content,
                      created_date=datetime.utcnow())


def test_register_document(database_service):
    article_record = get_article_record()
    database_service.register(
        article_record['document_id'],
        article_record
    )

    check_list = database_service.find({}, [], [])
    assert isinstance(check_list[0], dict)
    article_check = check_list[0]
    assert article_check['document_id'] == article_record['document_id']
    assert article_check['document_type'] == article_record['document_type']
    assert article_check['content'] == article_record['content']
    assert article_check['created_date'] is not None


@patch.object(ChangesService, 'register_change')
def test_register_document_register_change(mocked_register_change,
                                           database_service):
    article_record = get_article_record()
    database_service.register(
        article_record['document_id'],
        article_record
    )

    mocked_register_change.assert_called_with(article_record,
                                              ChangeType.CREATE)


def test_read_document(database_service):
    article_record = get_article_record({'Test': 'Test2'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    record_check = database_service.read(article_record['document_id'])
    assert record_check is not None
    assert record_check['document_id'] == article_record['document_id']
    assert record_check['document_type'] == article_record['document_type']
    assert record_check['content'] == article_record['content']
    assert record_check['created_date'] is not None


def test_db_failed(article_db_settings):
    article_db_settings['database_password'] = ''
    db_manager = CouchDBManager(**article_db_settings)
    with pytest.raises(
        DBFailed
    ):
        db_manager.database


def test_read_document_not_found(database_service):
    pytest.raises(
        DocumentNotFound,
        database_service.read,
        '336abebdd31894idnaoexistente'
    )


def test_update_document(database_service):
    article_record = get_article_record({'Test': 'Test3'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    article_update = database_service.read(article_record['document_id'])
    article_update['content'] = {'Test': 'Test3-updated'}
    database_service.update(
        article_record['document_id'],
        article_update
    )

    record_check = database_service.read(article_record['document_id'])
    assert record_check is not None
    assert record_check['document_id'] == article_update['document_id']
    assert record_check['document_type'] == article_update['document_type']
    assert record_check['content'] == article_update['content']
    assert record_check['created_date'] is not None
    assert record_check['updated_date'] is not None


@patch.object(ChangesService, 'register_change')
def test_update_document_register_change(mocked_register_change,
                                         database_service):
    article_record = get_article_record({'Test': 'Test3'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    article_update = database_service.read(article_record['document_id'])
    article_update['content'] = {'Test': 'Test3-updated'}
    database_service.update(
        article_record['document_id'],
        article_update
    )

    mocked_register_change.assert_called_with(article_update,
                                              ChangeType.UPDATE)


def test_update_document_not_found(database_service):
    article_record = get_article_record({'Test': 'Test4'})
    pytest.raises(
        DocumentNotFound,
        database_service.delete,
        article_record['document_id'],
        article_record
    )


def test_delete_document(database_service):
    article_record = get_article_record({'Test': 'Test5'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    record_check = database_service.read(article_record['document_id'])
    database_service.delete(
        article_record['document_id'],
        record_check
    )
    pytest.raises(DocumentNotFound,
                  database_service.read,
                  article_record['document_id'])


@patch.object(ChangesService, 'register_change')
def test_delete_document_register_change(mocked_register_change,
                                         database_service):
    article_record = get_article_record({'Test': 'Test5'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    record_check = database_service.read(article_record['document_id'])
    database_service.delete(
        article_record['document_id'],
        record_check
    )

    mocked_register_change.assert_called_with(record_check,
                                              ChangeType.DELETE)


def test_delete_document_not_found(database_service):
    article_record = get_article_record({'Test': 'Test6'})
    pytest.raises(
        DocumentNotFound,
        database_service.delete,
        article_record['document_id'],
        article_record
    )


def test_put_attachment_to_document(database_service, xml_test):
    article_record = get_article_record({'Test': 'Test7'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    file_id = "href_file"
    database_service.put_attachment(
        document_id=article_record['document_id'],
        file_id=file_id,
        content=xml_test.encode('utf-8'),
        file_properties={
            'content_type': "text/xml",
            'content_size': len(xml_test)
        }
    )

    record_check = dict(
        database_service.db_manager.database[article_record['document_id']]
    )
    assert record_check is not None
    assert file_id in database_service.db_manager.list_attachments(
        article_record['document_id']
    )


def test_put_attachment_to_document_update_dates(database_service,
                                                 xml_test):
    article_record = get_article_record({'Test': 'Test9'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    record_v1 = database_service.read(article_record['document_id'])
    dates_v1 = record_v1.get('created_date'), record_v1.get('updated_date')

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

    record_v2 = database_service.read(article_record['document_id'])
    dates_v2 = record_v2.get('created_date'), record_v2.get('updated_date')
    assert dates_v1[0] == dates_v2[0]
    assert dates_v1[1] is None
    assert dates_v2[1] > dates_v1[0]


def test_put_attachment_to_document_not_found(database_service,
                                              xml_test):
    article_record = get_article_record({'Test': 'Test8'})
    pytest.raises(
        DocumentNotFound,
        database_service.put_attachment,
        article_record['document_id'],
        "filename",
        xml_test.encode('utf-8'),
        {
            'content_type': "text/xml",
            'content_size': len(xml_test)
        }
    )


def test_read_document_with_attachments(database_service, xml_test):
    article_record = get_article_record({'Test': 'Test10'})
    file_id = "href_file"
    attachment_list = [
        file_id + str(cont)
        for cont in range(3)
    ]
    database_service.register(
        article_record['document_id'],
        article_record
    )
    for file_id in attachment_list:
        database_service.put_attachment(
            document_id=article_record['document_id'],
            file_id=file_id,
            content=xml_test.encode('utf-8'),
            file_properties={
                'content_type': "text/xml",
                'content_size': len(xml_test)
            }
        )

    record_check = database_service.read(article_record['document_id'])
    assert record_check is not None
    for attachment in attachment_list:
        assert attachment in record_check['attachments']


def test_get_attachment_from_document(database_service, xml_test):
    article_record = get_article_record({'Test': 'Test11'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    database_service.put_attachment(
        document_id=article_record['document_id'],
        file_id="href_file",
        content=xml_test.encode('utf-8'),
        file_properties={
            'content_type': "text/xml",
            'content_size': len(xml_test)
        }
    )

    attachment = database_service.get_attachment(
        document_id=article_record['document_id'],
        file_id="href_file"
    )
    assert attachment == xml_test.encode('utf-8')


def test_get_attachment_from_document_not_found(database_service,
                                                xml_test):
    article_record = get_article_record({'Test': 'Test12'})
    pytest.raises(
        DocumentNotFound,
        database_service.get_attachment,
        article_record['document_id'],
        "filename"
    )


def test_get_attachment_not_found(database_service, xml_test):
    article_record = get_article_record({'Test': 'Test13'})
    file_id = "href_file"
    attachment_list = [
        file_id + str(cont)
        for cont in range(3)
    ]
    database_service.register(
        article_record['document_id'],
        article_record
    )
    for file_id in attachment_list:
        database_service.put_attachment(
            document_id=article_record['document_id'],
            file_id=file_id,
            content=xml_test.encode('utf-8'),
            file_properties={
                'content_type': "text/xml",
                'content_size': len(xml_test)
            }
        )

    attachment = database_service.get_attachment(
        article_record['document_id'],
        "filename"
    )
    assert attachment is not None
    assert len(attachment.getvalue()) == 0


def test_sort_result():
    sort = []
    sort.append({'num': 'asc'})
    sort.append({'name': 'asc'})
    sort.append({'type': 'asc'})
    results = []
    results.append({'name': 'Ana', 'num': 200, 'type': 'B'})
    results.append({'name': 'Ana', 'num': 500, 'type': 'A'})
    results.append({'name': 'F', 'num': 500, 'type': 'A'})
    results.append({'name': 'F', 'num': 200, 'type': 'B'})
    expected = []
    expected.append({'name': 'Ana', 'num': 200, 'type': 'B'})
    expected.append({'name': 'F', 'num': 200, 'type': 'B'})
    expected.append({'name': 'Ana', 'num': 500, 'type': 'A'})
    expected.append({'name': 'F', 'num': 500, 'type': 'A'})
    got = sort_results(results, sort)
    assert expected == got

    sort = []
    sort.append({'name': 'asc'})
    sort.append({'type': 'asc'})
    sort.append({'num': 'asc'})
    expected = []
    expected.append({'name': 'Ana', 'num': 500, 'type': 'A'})
    expected.append({'name': 'Ana', 'num': 200, 'type': 'B'})
    expected.append({'name': 'F', 'num': 500, 'type': 'A'})
    expected.append({'name': 'F', 'num': 200, 'type': 'B'})
    got = sort_results(results, sort)
    assert expected == got

    sort = []
    sort.append({'type': 'asc'})
    sort.append({'name': 'asc'})
    sort.append({'num': 'asc'})
    expected = []
    expected.append({'name': 'Ana', 'num': 500, 'type': 'A'})
    expected.append({'name': 'F', 'num': 500, 'type': 'A'})
    expected.append({'name': 'Ana', 'num': 200, 'type': 'B'})
    expected.append({'name': 'F', 'num': 200, 'type': 'B'})
    got = sort_results(results, sort)
    assert expected == got

    sort = []
    sort.append({'type': 'desc'})
    sort.append({'name': 'asc'})
    sort.append({'num': 'asc'})
    expected = []
    expected.append({'name': 'Ana', 'num': 200, 'type': 'B'})
    expected.append({'name': 'F', 'num': 200, 'type': 'B'})
    expected.append({'name': 'Ana', 'num': 500, 'type': 'A'})
    expected.append({'name': 'F', 'num': 500, 'type': 'A'})
    got = sort_results(results, sort)
    assert expected == got

    sort = []
    sort.append({'num': 'desc'})
    sort.append({'type': 'desc'})
    sort.append({'name': 'asc'})
    results = []
    results.append({'name': 'Ana', 'num': 200, 'type': 'B'})
    results.append({'name': 'Ana', 'num': 500, 'type': 'A'})
    results.append({'name': 'F', 'num': 500, 'type': 'A'})
    results.append({'name': 'F', 'num': 200, 'type': 'Z'})
    expected = []
    expected.append({'name': 'Ana', 'num': 500, 'type': 'A'})
    expected.append({'name': 'F', 'num': 500, 'type': 'A'})
    expected.append({'name': 'F', 'num': 200, 'type': 'Z'})
    expected.append({'name': 'Ana', 'num': 200, 'type': 'B'})
    got = sort_results(results, sort)
    assert expected == got


def test_add_attachment_properties(database_service, xml_test):
    file_properties1 = {
            'content_type': "text/xml",
            'content_size': len(xml_test)
        }
    key = database_service.db_manager._attachments_properties_key
    expected = {}
    expected[key] = {
        'file1': file_properties1,
    }

    article_record = get_article_record({'Test': 'Test13'})
    database_service.register(
        article_record['document_id'],
        article_record
    )

    database_service.db_manager \
        .add_attachment_properties_to_document_record(
            article_record,
            'file1',
            file_properties1
        )
    assert expected[key] == article_record[key]


def test_get_attachment_properties(database_service, xml_test):

    article_record = get_article_record({'Test': 'Test11'})
    database_service.register(
        article_record['document_id'],
        article_record
    )
    file_properties = {
            'content_type': "text/xml",
            'content_size': len(xml_test)
        }

    database_service.put_attachment(
        document_id=article_record['document_id'],
        file_id='href_file',
        content=xml_test.encode('utf-8'),
        file_properties=file_properties
    )

    database_service.put_attachment(
        document_id=article_record['document_id'],
        file_id='href_file2',
        content=xml_test.encode('utf-8'),
        file_properties=file_properties
    )
    expected = file_properties
    assert expected == \
        database_service.db_manager.get_attachment_properties(
            article_record['document_id'],
            'href_file'
        )


def test_find_documents_by_selected_field_returns_according_to_filter(
    database_service,
    test_documents_records,
    find_criteria_result
):
    find_args, expected = find_criteria_result
    for document_record in test_documents_records:
        database_service.db_manager.create(document_record['document_id'],
                                           document_record)

    check_list = database_service.db_manager.find(**find_args)
    assert isinstance(check_list[0], dict)
    assert len(check_list) == len(expected)
    for check_document, expected_document in zip(check_list, expected):
        compare_documents(check_document, expected_document)


def compare_documents(document, expected):
    if document == expected:
        assert document == expected
    elif len(document) == len(expected) + 1:
        # para ignorar "revision"
        for k in expected.keys():
            assert document[k] == expected[k]
    else:
        assert document == expected


def test_add_file_insert_file_into_database_ok(
    db_manager_test,
    xml_test
):
    db_manager_test.insert_file(
        file_id='href_file1',
        content=xml_test.encode('utf-8')
    )
    file = db_manager_test.database.get(
        '/'.join([db_manager_test._database_url, 'href_file1'])
    )
    assert file is not None


def test_add_file_call_dbmanager_insert_file(database_service, xml_test):
    with patch.object(database_service.db_manager, 'insert_file') \
            as mocked_insert_file:
        database_service.add_file(
            file_id='href_file1',
            content=xml_test.encode('utf-8'),
        )
        mocked_insert_file.assert_called_once_with(
            file_id='href_file1',
            content=xml_test.encode('utf-8')
        )


def test_add_file_call_changeservice_register(inmemory_db_setup, xml_test):
    with patch.object(inmemory_db_setup.changes_service, 'register') \
            as mocked_change_register:
        file_id = '/rawfile/href_file1'
        inmemory_db_setup.add_file(
            file_id=file_id,
            content=xml_test.encode('utf-8'),
        )
        mocked_change_register.assert_called_once_with(
            file_id, ChangeType.CREATE
        )


def test_add_file_dbmanager_insert_into_database(inmemory_db_setup, xml_test):
    inmemory_db_setup.add_file(
        file_id='href_file1',
        content=xml_test.encode('utf-8'),
    )
    file = inmemory_db_setup.db_manager.database.get(
        '/'.join([inmemory_db_setup.db_manager._database_url, 'href_file1'])
    )
    assert file is not None
