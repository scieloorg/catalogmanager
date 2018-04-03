import os
from unittest.mock import patch

from catalog_persistence.databases import (
    InMemoryDBManager,
    DatabaseService,
    DocumentNotFound
)
from catalog_persistence.models import (
    RecordType,
)

from catalogmanager.article_services import(
    ArticleServices,
)


def get_files():
    xml_filename = './packages/0034-8910-rsp-S01518-87872016050006741/0034-8910-rsp-S01518-87872016050006741.xml'
    files = [item for item in os.listdir('./packages/0034-8910-rsp-S01518-87872016050006741/') if not item.endswith('.xml')]
    return (xml_filename, files)


# def test_article_reception():
#     xml_filename, files = get_files()
#
#     expected = {
#         'document_id': '336abebdd31894idnaoexistente',
#         'document_type': RecordType.ARTICLE.value,
#         'content': {'Test': 'Test4'},
#         'created_date': '01010101'
#     }
#
#     article = Article(xml, files)
#     article_record = expected
#
#         db_service.register(
#             article.id, article_record)
#         db_service.register_attachment(
#             document_id=article.id,
#             attach_name=article.xml_tree.basename,
#             content=article.xml_tree.filename
#             )
#         if files is not None:
#             for f in files:
#                 db_service.register_attachment(
#                     document_id=article.id,
#                     attach_name=os.path.basename(f),
#                     content=f
#                     )
#         return self.article_data_services.location(article.id)
#
#     changes_db_manager = InMemoryDBManager({'database_name': 'changes'})
#     articles_db_manager = InMemoryDBManager({'database_name': 'articles'})
#
#     article_services = ArticleServices(
#         articles_db_manager, changes_db_manager)
#     gotten = article_services.receive(xml_filename, files)
#     assert expected == gotten


@patch.object(DatabaseService, 'read')
def test_get_article_in_database(mocked_dataservices_read,
                                 change_service,
                                 inmemory_article_location):
    _, _, article_id = inmemory_article_location.split('/')
    mocked_dataservices_read.return_value = {'document_id': article_id}
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_check = article_services.get_article_data(article_id)
    assert article_check is not None
    assert isinstance(article_check, dict)
    mocked_dataservices_read.assert_called_with(article_id)


@patch.object(DatabaseService, 'read', side_effect=DocumentNotFound)
def test_get_article_in_database_not_found(mocked_dataservices_read,
                                           change_service,
                                           inmemory_article_location):
    _, _, article_id = inmemory_article_location.split('/')
    mocked_dataservices_read.return_value = {'document_id': article_id}
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_check = article_services.get_article_data(article_id)
    assert article_check is None


def test_get_article_record(change_service,
                            inmemory_article_location,
                            article_files):
    _, _, article_id = inmemory_article_location.split('/')
    article_services = ArticleServices(
        change_service[0],
        change_service[1]
    )
    article_check = article_services.get_article_data(article_id)
    assert article_check is not None
    assert isinstance(article_check, dict)
    assert article_check.get('document_id') == article_id
    assert article_check.get('document_type') == RecordType.ARTICLE.value
    assert article_check.get('content') is not None
    assert isinstance(article_check['content'], dict)
    assert article_check.get('created_date') is not None
    assert article_check.get('attachments') is not None
    assert isinstance(article_check['attachments'], list)
