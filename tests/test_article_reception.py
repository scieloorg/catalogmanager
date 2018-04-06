import os
from unittest.mock import patch

import pytest

from catalog_persistence.databases import (
    DatabaseService,
    DocumentNotFound
)
from catalog_persistence.models import (
    RecordType,
)
from catalogmanager.article_services import (
    ArticleServices,
    ArticleServicesException
)


def get_files():
    xml_filename = './packages/0034-8910-rsp-S01518-87872016050006741/0034-8910-rsp-S01518-87872016050006741.xml'
    files = [item for item in os.listdir('./packages/0034-8910-rsp-S01518-87872016050006741/') if not item.endswith('.xml')]
    return (xml_filename, files)


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
    pytest.raises(
        ArticleServicesException,
        article_services.get_article_data,
        article_id
    )


def test_get_article_record(change_service,
                            inmemory_article_location,
                            article_file,
                            assets_files):
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
    assert article_check['content'].get('xml_name') is not None
    assert article_check.get('created_date') is not None
    assert article_check.get('attachments') is not None
    assert isinstance(article_check['attachments'], list)
