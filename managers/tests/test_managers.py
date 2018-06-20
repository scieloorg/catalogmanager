
from unittest.mock import patch

import pytest

import managers
from persistence.services import DatabaseService
from managers.article_manager import ArticleManager


@patch.object(managers, '_get_changes_services')
@patch.object(DatabaseService, 'list_changes')
def test_list_changes_return_from_changeservice_list_changes(
    mocked_list_changes,
    mocked_changes_services,
    changes_service,
    list_changes_expected
):
    mocked_changes_services.return_value = \
        changes_service
    mocked_list_changes.return_value = list_changes_expected
    changes = managers.list_changes(last_sequence='1', limit=10)
    mocked_list_changes.assert_called_once_with(
        last_sequence='1',
        limit=10
    )
    assert changes == list_changes_expected


def test_create_file_succeeded(test_package_A):
    xml_file = test_package_A[0]
    file = managers.create_file(filename=xml_file.name,
                                content=xml_file.content)
    assert file is not None
    assert isinstance(file, managers.models.file.File)


def test_get_article_manager(database_config):
    db_config = {
        'database_uri': '{}:{}'.format(
            database_config['db_host'],
            database_config['db_port']
        ),
        'database_username': database_config['username'],
        'database_password': database_config['password'],
    }
    article_manager = managers._get_article_manager(
        **db_config
    )
    assert article_manager is not None
    assert isinstance(article_manager, managers.article_manager.ArticleManager)
    assert article_manager.article_db_service is not None
    assert isinstance(article_manager.article_db_service, DatabaseService)
    assert article_manager.file_db_service is not None
    assert isinstance(article_manager.file_db_service, DatabaseService)


@patch.object(managers, '_get_article_manager')
@patch.object(managers.models.article_model.ArticleDocument, 'add_version')
def test_post_article_file_error(mocked_article_add_version,
                                 mocked__get_article_manager,
                                 test_package_A,
                                 set_inmemory_article_manager):
    mocked__get_article_manager.return_value = set_inmemory_article_manager
    error_msg = 'Invalid XML Content'
    mocked_article_add_version.side_effect = \
        managers.models.article_model.InvalidXMLContent()
    with pytest.raises(managers.exceptions.ManagerFileError) as excinfo:
        managers.post_article(
            article_id='ID-post-article-123',
            xml_id=test_package_A[0].name,
            xml_file=test_package_A[0].content,
            **{}
        )
    assert excinfo.value.message == error_msg


@patch.object(managers, '_get_article_manager')
@patch.object(ArticleManager, 'add_document')
def test_post_article_insert_file_to_database_error(
    mocked_article_manager_add,
    mocked__get_article_manager,
    test_package_A,
    set_inmemory_article_manager
):
    mocked__get_article_manager.return_value = set_inmemory_article_manager
    error_msg = 'Database Error'
    mocked_article_manager_add.side_effect = \
        managers.article_manager.ArticleManagerException(message=error_msg)

    with pytest.raises(managers.article_manager.ArticleManagerException) \
            as excinfo:
        managers.post_article(
            article_id='ID-post-article-123',
            xml_id=test_package_A[0].name,
            xml_file=test_package_A[0].content,
            **{}
        )
    assert excinfo.value.message == error_msg


@patch.object(managers, '_get_article_manager')
def test_post_article_insert_file_to_database_ok(
    mocked__get_article_manager,
    test_package_A,
    set_inmemory_article_manager
):
    xml_file = test_package_A[0]
    mocked__get_article_manager.return_value = set_inmemory_article_manager

    article_url = managers.post_article(
        article_id='ID-post-article-123',
        xml_id=xml_file.name,
        xml_file=xml_file.content,
        **{}
    )
    assert article_url is not None
    assert article_url.endswith(xml_file.name)
