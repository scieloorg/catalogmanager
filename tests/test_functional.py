
import io
import os
from collections import OrderedDict

import webtest
from lxml import etree


def test_add_article_register_change(testapp, test_package_A):
    article_id = 'ID-post-article-123'
    url = '/articles/{}'.format(article_id)

    # Um documento é registrado no módulo de persistencia. Ex: Artigo
    xml_file_path, assets_files = test_package_A[0], test_package_A[1:]
    changes_expected = {
        'results': [],
        'latest': 1
    }
    assets_field = []
    for article_file in assets_files:
        article_filename = os.path.basename(article_file)
        with open(article_file, 'rb') as fb:
            file_content = fb.read()
            assets_field.append(('asset_field',
                                 article_filename,
                                 file_content))
            latest = int(changes_expected['latest']) + 1
            changes_expected['results'].append(
                {
                    'change_id': '{:0>17}'.format(latest),
                    'document_id': article_id,
                    'document_type': 'ART',
                    'type': 'UPDATE'
                }
            )
            changes_expected['latest'] = latest
    params = OrderedDict([
        ("article_id", article_id),
        ("xml_file", webtest.forms.Upload(xml_file_path))
    ])
    result = testapp.put(url,
                         params=params,
                         upload_files=assets_field,
                         content_type='multipart/form-data')
    assert result.status_code == 201

    changes_expected['results'].insert(0,
                                       {
                                           'change_id': '1'.zfill(20),
                                           'document_id': article_id,
                                           'document_type': 'ART',
                                           'type': 'CREATE'
                                       })
    # Checa se é possível recuperar o registro do documento pelo id
    result = testapp.get(url)
    assert result.status_code == 200
    assert result.json is not None
    res_dict = result.json
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
        '{}/assets/{}'.format(url, os.path.basename(asset_file))
        for asset_file in assets_files
    ]
    for expected_href in expected_hrefs:
        assert expected_href in xml_nodes

    # Deve ser possível recuperar os registros de mudanças do documento de
    # acordo com os parâmetros informados no serviço
    last_sequence = ''
    limit = 10
    result = testapp.get('/changes?since={}&limit={}'.format(last_sequence,
                                                             limit))
    assert result.status_code == 200
    assert result.json is not None
    assert len(result.json) > len(changes_expected['results'])
    for resp_result, expected in zip(result.json, changes_expected['results']):
        assert resp_result['document_id'] == expected['document_id']
        assert resp_result['document_type'] == expected['document_type']
        assert resp_result['type'] == expected['type']

    # Sequencial das mudanças ainda não implementado
    # last_sequence = result.json[-1]['change_id']
    # result = testapp.get('/changes?since={}&limit={}'.format(last_sequence,
    #                                                          limit))
    # assert result.status_code == 200
    # assert result.json is not None
    # assert len(result.json) == 0
