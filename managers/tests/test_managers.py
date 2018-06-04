
import hashlib
from unittest.mock import patch

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


@patch.object(ArticleManager, 'add_document')
def test_post_article(
    mocked_article_manager_add,
    test_package_A,
    database_config
):
    checksum = hashlib.sha1(test_package_A[0].content).hexdigest()
    expected = '/'.join([checksum[:13], test_package_A[0].name])
    db_settings = {
        'database_uri': '{}:{}'.format(
            database_config['db_host'],
            database_config['db_port']
        ),
        'database_username': database_config['username'],
        'database_password': database_config['password'],
    }
    result = managers.post_article(
        xml_file=test_package_A[0],
        **db_settings
    )
    mocked_article_manager_add.assert_called_once()
    assert result is not None
    assert result == expected
