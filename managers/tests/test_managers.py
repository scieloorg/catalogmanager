
from unittest.mock import patch

import managers
from persistence.services import DatabaseService


@patch.object(managers, '_get_changes_dbmanager')
@patch.object(DatabaseService, 'list_changes')
def test_list_changes_return_from_changeservice_list_changes(
    mocked_list_changes,
    mocked_changes_dbmanager,
    change_service,
    list_changes_expected
):
    mocked_changes_dbmanager.return_value = change_service[1]
    mocked_list_changes.return_value = list_changes_expected
    changes = managers.list_changes(last_sequence='1', limit=10)
    mocked_list_changes.assert_called_once_with(
        last_sequence='1',
        limit=10
    )
    assert changes == list_changes_expected