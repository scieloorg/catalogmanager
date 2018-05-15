from datetime import datetime
from unittest.mock import patch

from pyramid import testing

from catalogmanager_api.views.change import ChangeAPI


@patch('catalogmanager.list_changes')
def test_change_api_collection_post_calls_list_changes(mocked_list_changes,
                                                       db_settings,
                                                       testapp):
    request = testing.DummyRequest()
    request.POST = {
        'last_sequence': 'SEQ123456',
        'limit': 100,
    }
    request.db_settings = db_settings
    ChangeAPI.collection_post(ChangeAPI(request))

    mocked_list_changes.assert_called_once_with(
        last_sequence=request.POST['last_sequence'],
        limit=request.POST['limit'],
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
            "document_type": "ARTICLE",
            "content": {
                'xml': "ID-{}.xml".format(id),
                'assets': [
                    "{}-{}.png".format(id, asset_id) for asset_id in range(3)
                ]
            }
        }
        for id in range(123457, 123466)
    ]
    mocked_list_changes.return_value = expected
    request = testing.DummyRequest()
    request.POST = {
        'last_sequence': 'SEQ123456',
        'limit': 100,
    }
    request.db_settings = db_settings
    response = ChangeAPI.collection_post(ChangeAPI(request))
    assert response.status_code == 200
    assert response.json == expected
