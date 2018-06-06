from unittest.mock import patch

from api.views.change import ChangeAPI


@patch('managers.list_changes')
def test_change_api_collection_post_calls_list_changes(mocked_list_changes,
                                                       dummy_request):
    dummy_request.GET = {
        'since': '123456',
        'limit': 100,
    }
    ChangeAPI.collection_get(ChangeAPI(dummy_request))

    mocked_list_changes.assert_called_once_with(
        last_sequence=dummy_request.GET['since'],
        limit=dummy_request.GET['limit'],
        **dummy_request.db_settings
    )


@patch('managers.list_changes')
def test_change_api_collection_post_return_changes_list(mocked_list_changes,
                                                        dummy_request):
    expected = [
        {
            "change_id": "{}".format(id),
            "document_id": "ID-{}".format(id),
            "document_type": "ART",
            "type": "CREATE"
        }
        for id in range(123457, 123466)
    ]
    mocked_list_changes.return_value = expected
    dummy_request.GET = {
        'since': '123456',
        'limit': 100,
    }
    response = ChangeAPI.collection_get(ChangeAPI(dummy_request))
    assert response.status_code == 200
    assert response.json == expected
