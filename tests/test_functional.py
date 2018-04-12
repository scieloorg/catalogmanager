
from collections import OrderedDict

import pytest
import webtest

from catalogmanager_api import main

from .conftest import (
    PKG_A,
)


@pytest.fixture
def testapp():
    settings = {'ini_filename': 'development.ini'}
    test_app = main(settings)
    return webtest.TestApp(test_app)


def test_add_article_register_change(testapp):
    article_id = 'ID-post-article-123'
    url = '/articles/{}'.format(article_id)

    # Um documento é registrado no módulo de persistencia. Ex: Artigo
    xml_file_path, xml_assets_files = PKG_A[0], PKG_A[1:]
    params = OrderedDict([
        ("article_id", article_id),
        ("xml_file", webtest.forms.Upload(xml_file_path))
    ])
    result = testapp.put(url,
                         params=params,
                         content_type='multipart/form-data')
    assert result.status_code == 200

    # Checa se é possível recuperar o registro do documento pelo id
    result = testapp.get(url)
    assert result.status_code == 200
    assert result.json is not None
    assert result.json.get("document_id") == article_id
    assert result.json.get("content") is not None
    assert result.json["content"]["xml"] == xml_file_path

    # Deve ser possível ter uma URL para resgatar o arquivo XML
    # xml_url = '{}/{}'.format(url, )

    # Checa se a lista de mudanças trás o registro de mundança do registro do
    # documento
