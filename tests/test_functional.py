
import os
import io
import json
from collections import OrderedDict

import pytest
import webtest
from lxml import etree

from catalogmanager_api import main
from .conftest import (
    PKG_A,
)


@pytest.fixture
def testapp():
    settings = {'__file__': 'development.ini'}
    test_app = main(settings)
    return webtest.TestApp(test_app)


def test_add_article_register_change(testapp, setup_couchdb):
    article_id = 'ID-post-article-123'
    url = '/articles/{}'.format(article_id)

    # Um documento é registrado no módulo de persistencia. Ex: Artigo
    xml_file_path, assets_files = PKG_A[0], PKG_A[1:]
    assets_field = []
    for article_file in assets_files:
        with open(article_file, 'rb') as fb:
            file_content = fb.read()
            assets_field.append(('asset_field',
                                 os.path.basename(article_file),
                                 file_content))
    params = OrderedDict([
        ("article_id", article_id),
        ("xml_file", webtest.forms.Upload(xml_file_path))
    ])
    result = testapp.put(url,
                         params=params,
                         upload_files=assets_field,
                         content_type='multipart/form-data')
    assert result.status_code == 200

    # Checa se é possível recuperar o registro do documento pelo id
    result = testapp.get(url)
    assert result.status_code == 200
    assert result.json is not None
    res_dict = json.loads(result.json)
    assert res_dict.get("document_id") == article_id
    assert res_dict.get("content") is not None
    assert res_dict["content"]["xml"] == os.path.basename(xml_file_path)
    res_assets = res_dict["content"].get("assets")
    assert isinstance(res_assets, list)
    for asset_file in assets_files:
        assert os.path.basename(asset_file) in res_assets

    # Deve ser possível ter uma URL para resgatar o arquivo XML e os ativos
    # digitais
    xml_url = '{}/xml'.format(url)
    result = testapp.get(xml_url)
    assert result.status_code == 200
    assert result.body is not None
    xml_tree = etree.parse(io.BytesIO(result.body))
    xpath = '{http://www.w3.org/1999/xlink}href'
    xml_nodes = [
        node.get(xpath)
        for node in xml_tree.findall('.//*[@{}]'.format(xpath))
    ]
    expected_hrefs = [
        '{}/{}'.format(url, os.path.basename(asset_file))
        for asset_file in assets_files
    ]
    for expected_href in expected_hrefs:
        assert expected_href in xml_nodes
