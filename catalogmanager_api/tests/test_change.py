from unittest.mock import patch

from pyramid import testing

from catalogmanager_api.views.change import ChangeAPI


@patch('catalogmanager.list_changes')
def test_change_api_collection_post_calls_list_changes(mocked_list_changes,
                                                       db_settings,
                                                       testapp):
    request = testing.DummyRequest()
    request.GET = {
        'since': 'SEQ123456',
        'limit': 100,
    }
    request.db_settings = db_settings
    ChangeAPI.collection_get(ChangeAPI(request))

    mocked_list_changes.assert_called_once_with(
        last_sequence=request.GET['since'],
        limit=request.GET['limit'],
        **db_settings
    )


@patch('catalogmanager.list_changes')
def test_change_api_collection_post_return_changes_list(mocked_list_changes,
                                                        db_settings,
                                                        testapp):
    expected = [
        {
            "change_id": "SEQ{}".format(id),
            "document_id": "ID-{}".format(id),
            "document_type": "ART",
            "type": "CREATE"
        }
        for id in range(123457, 123466)
    ]
    mocked_list_changes.return_value = expected
    request = testing.DummyRequest()
    request.GET = {
        'since': 'SEQ123456',
        'limit': 100,
    }
    request.db_settings = db_settings
    response = ChangeAPI.collection_get(ChangeAPI(request))
    assert response.status_code == 200
    assert response.json == expected
