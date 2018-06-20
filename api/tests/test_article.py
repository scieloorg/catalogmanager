from io import BytesIO
from unittest.mock import patch

import pytest
from lxml import etree
from pyramid.httpexceptions import (
    HTTPInternalServerError,
    HTTPNotFound,
    HTTPBadRequest,
    HTTPServiceUnavailable,
)
from webob.multidict import MultiDict

import managers
from api.views.article import (
    ArticleAPI,
    ArticleXML,
    ArticleAsset,
    ArticleManifest,
)
from managers.models.article_model import ArticleDocument
from persistence.databases import DBFailed


def _get_file_property(filename, content, size):
    return {
        'filename': filename,
        'content': content,
        'content_size': size
    }


class MockCGIFieldStorage(object):

    def __init__(self, name, file):
        self.filename = name
        self.file = file


@patch.object(managers, 'get_article_data')
def test_http_get_article_not_found(mocked_get_article_data, dummy_request):
    article_id = 'ID123456'
    error_msg = 'Article {} not found'.format(article_id)
    mocked_get_article_data.side_effect = \
        managers.article_manager.ArticleManagerException(
            message=error_msg
        )
    dummy_request.matchdict = {'id': article_id}

    article_api = ArticleAPI(dummy_request)
    with pytest.raises(HTTPNotFound) as excinfo:
        article_api.get()
    assert excinfo.value.message == error_msg


@patch.object(managers, 'get_article_data')
def test_http_get_article_succeeded(mocked_get_article_data, dummy_request):
    article_id = 'ID123456'
    expected = {
        "document_id": article_id,
        "document_type": "ART",
        "content": {
            'xml': "test.xml",
            'assets': ["img1.png", "img2.png", "img3.png"]
        },
    }
    mocked_get_article_data.return_value = expected
    dummy_request.matchdict = {'id': article_id}

    article_api = ArticleAPI(dummy_request)
    response = article_api.get()
    assert response.status == '200 OK'
    assert response.json == expected


@patch.object(managers, 'get_article_file')
def test_http_get_xml_file_article_not_found(mocked_get_article_file,
                                             dummy_request):
    article_id = 'ID123456'
    error_msg = 'Article {} not found'.format(article_id)
    mocked_get_article_file.side_effect = \
        managers.article_manager.ArticleManagerException(
            message=error_msg
        )
    dummy_request.matchdict = {'id': article_id}

    article_xml = ArticleXML(dummy_request)
    with pytest.raises(HTTPNotFound) as excinfo:
        article_xml.get()
    assert excinfo.value.message == error_msg


@patch.object(managers, 'get_article_file')
def test_http_get_xml_file_not_found(mocked_get_article_file, dummy_request):
    article_id = 'ID123456'
    error_msg = 'Missing XML file {}'.format(article_id)
    mocked_get_article_file.side_effect = \
        managers.article_manager.ArticleManagerException(
            message=error_msg
        )
    dummy_request.matchdict = {'id': article_id}

    article_xml = ArticleXML(dummy_request)
    with pytest.raises(HTTPNotFound) as excinfo:
        article_xml.get()
    assert excinfo.value.message == error_msg


@patch.object(managers, 'get_article_file')
@patch.object(managers, 'get_article_data')
def test_http_get_xml_file_calls_get_article_data(mocked_get_article_data,
                                                  mocked_get_article_file,
                                                  dummy_request,
                                                  test_xml_file):
    article_id = 'ID123456'
    mocked_get_article_file.return_value = test_xml_file.encode('utf-8')
    dummy_request.matchdict = {'id': article_id}

    article_xml = ArticleXML(dummy_request)
    article_xml.get()
    mocked_get_article_data.assert_called_once_with(
        article_id=article_id,
        **dummy_request.db_settings
    )


@patch.object(managers, 'get_article_file')
@patch.object(managers, 'get_article_data')
@patch.object(managers, 'set_assets_public_url')
def test_http_get_xml_file_calls_set_assets_public_url_if_there_is_assets(
    mocked_set_assets_public_url,
    mocked_get_article_data,
    mocked_get_article_file,
    dummy_request,
    test_article_files,
    test_xml_file
):
    article_id = 'ID123456'
    assets = [
        asset_file.name
        for asset_file in test_article_files[1:]
    ]
    mocked_get_article_data.return_value = {
        "document_id": article_id,
        "document_type": "ART",
        "content": {
            'xml': test_article_files[0],
            'assets': assets
        },
    }
    mocked_get_article_file.return_value = test_xml_file.encode('utf-8')
    mocked_set_assets_public_url.return_value = b'Test123'
    dummy_request.matchdict = {'id': article_id}
    article_xml = ArticleXML(dummy_request)
    article_xml.get()
    mocked_set_assets_public_url.assert_called_once_with(
        article_id=article_id,
        xml_content=test_xml_file.encode('utf-8'),
        assets_filenames=assets,
        public_url='/articles/{}/assets/{}'
    )


@patch.object(managers, 'get_article_file')
@patch.object(managers, 'get_article_data')
@patch.object(managers, 'set_assets_public_url')
def test_http_get_xml_file_doesnt_calls_set_assets_public_url_if_no_assets(
    mocked_set_assets_public_url,
    mocked_get_article_data,
    mocked_get_article_file,
    dummy_request,
    test_article_files,
    test_xml_file
):
    article_id = 'ID123456'
    mocked_get_article_data.return_value = {
        "document_id": article_id,
        "document_type": "ART",
        "content": {
            'xml': "test.xml",
        },
    }
    mocked_get_article_file.return_value = test_xml_file.encode('utf-8')
    dummy_request.matchdict = {'id': article_id}
    article_xml = ArticleXML(dummy_request)
    article_xml.get()
    mocked_set_assets_public_url.assert_not_called()


@patch.object(managers, 'get_article_file')
@patch.object(managers, 'get_article_data')
def test_http_get_xml_file_succeeded(mocked_get_article_data,
                                     mocked_get_article_file,
                                     dummy_request,
                                     test_article_files,
                                     test_xml_file):
    #XXX este é um típico teste funcional e deveria ser implementado usando
    #fixtures e implementações reais. O uso de patches praticamente invalida
    #este teste.
    article_id = 'ID123456'
    assets = [
        asset_file.name
        for asset_file in test_article_files[1:]
    ]
    expected_hrefs = [
        '/articles/{}/assets/{}'.format(article_id, asset_file.name)
        for asset_file in test_article_files[1:]
    ]
    mocked_get_article_data.return_value = {
        "document_id": article_id,
        "document_type": "ART",
        "content": {
            'xml': test_article_files[0],
            'assets': assets
        },
    }
    mocked_get_article_file.return_value = test_xml_file.encode('utf-8')
    dummy_request.matchdict = {'id': article_id}

    article_xml = ArticleXML(dummy_request)
    response = article_xml.get()
    assert response.status == '200 OK'
    assert response.content_type == 'application/xml'
    assert response.body is not None
    xml_tree = etree.parse(BytesIO(response.body))
    xpath = '{http://www.w3.org/1999/xlink}href'
    xml_nodes = [
        node.get(xpath)
        for node in xml_tree.findall('.//*[@{}]'.format(xpath))
    ]
    for expected_href in expected_hrefs:
        assert expected_href in xml_nodes


@patch.object(managers, 'put_article')
def test_http_article_calls_put_article_service_error(mocked_put_article,
                                                      dummy_request,
                                                      test_xml_file):
    xml_file = MockCGIFieldStorage("test_xml_file.xml",
                                   BytesIO(test_xml_file.encode('utf-8')))
    error_msg = 'Missing XML file {}'.format("test_xml_file")
    mocked_put_article.side_effect = \
        managers.article_manager.ArticleManagerException(
            message=error_msg
        )
    dummy_request.POST = MultiDict(
        [('id', xml_file.filename), ('xml_file', xml_file)]
    )

    article_api = ArticleAPI(dummy_request)
    with pytest.raises(HTTPInternalServerError) as excinfo:
        article_api.put()
    assert excinfo.value.message == error_msg


@patch.object(managers, 'put_article')
def test_http_article_put_article_succeeded(mocked_put_article,
                                            dummy_request,
                                            test_xml_file):
    xml_file = MockCGIFieldStorage("test_xml_file.xml",
                                   BytesIO(test_xml_file.encode('utf-8')))
    dummy_request.POST = MultiDict(
        [('id', xml_file.filename), ('xml_file', xml_file)]
    )

    article_api = ArticleAPI(dummy_request)
    response = article_api.put()
    assert response.status_code == 200
    assert response.json is not None
    assert response.json.get('url').endswith(xml_file.filename)


@patch.object(managers, 'put_article')
def test_http_article_put_article_with_assets(mocked_put_article,
                                              dummy_request,
                                              test_xml_file,
                                              test_article_files):
    #XXX aqui deveria ser um teste funcional simples, sem qualquer dublê de
    #testes (mocks e afins).
    xml_file = MockCGIFieldStorage("test_xml_file.xml",
                                   BytesIO(test_xml_file.encode('utf-8')))
    expected_assets_files = []
    assets_field = []
    for article_file in test_article_files[1:]:
        with open(article_file, 'rb') as fb:
            file_content = fb.read()
            expected_assets_files.append(
                _get_file_property(article_file.name,
                                   file_content,
                                   article_file.lstat().st_size),
            )
            assets_field.append(
                ('asset_field',
                 MockCGIFieldStorage(article_file.name, BytesIO(file_content)))
            )
    dummy_request.POST = MultiDict(
        [('id', xml_file.filename), ('xml_file', xml_file)] + assets_field
    )

    article_api = ArticleAPI(dummy_request)
    response = article_api.put()
    mocked_put_article.assert_called_once()
    assert response.status_code == 200
    assert response.json is not None
    assert response.json.get('url').endswith(xml_file.filename)


@patch.object(managers, 'get_asset_file')
def test_http_get_asset_file_calls_get_asset_file(mocked_get_asset_file,
                                                  dummy_request):
    article_id = 'ID123456'
    asset_id = 'ID123456'
    mocked_get_asset_file.return_value = '', b'123456Test'
    dummy_request.matchdict = {
        'id': article_id,
        'asset_id': asset_id
    }
    article_asset_api = ArticleAsset(dummy_request)
    response = article_asset_api.get()
    mocked_get_asset_file.assert_called_once_with(
        article_id=article_id,
        asset_id=asset_id,
        **dummy_request.db_settings
    )
    assert response.status_code == 200


@patch.object(managers, 'get_asset_file')
def test_http_get_asset_file_not_found(mocked_get_asset_file, dummy_request):
    article_id = 'ID123456'
    asset_id = 'a.jpg'
    error_msg = 'Asset {} (Article {}) not found'.format(asset_id, article_id)
    mocked_get_asset_file.side_effect = \
        managers.article_manager.ArticleManagerException(
            message=error_msg
        )
    dummy_request.matchdict = {
        'id': article_id,
        'asset_id': asset_id
    }
    article_asset_api = ArticleAsset(dummy_request)
    with pytest.raises(HTTPNotFound) as excinfo:
        article_asset_api.get()
    assert excinfo.value.message == error_msg


@patch.object(managers, 'get_asset_file')
def test_http_get_asset_file_succeeded(mocked_get_asset_file,
                                       dummy_request,
                                       test_xml_file):
    #XXX este teste deveria usar fixture num setup prévio ao invés de patch.
    article_id = 'ID123456'
    asset_id = 'a.jpg'
    expected = 'text/xml', test_xml_file.encode('utf-8')
    mocked_get_asset_file.return_value = expected
    dummy_request.matchdict = {
        'id': article_id,
        'asset_id': asset_id
    }
    article_asset_api = ArticleAsset(dummy_request)
    response = article_asset_api.get()
    assert response.status == '200 OK'
    assert response.body == expected[1]
    assert response.content_type == expected[0]


@patch.object(managers, 'post_article')
def test_post_article_invalid_xml(mocked_post_article,
                                  dummy_request,
                                  test_xml_file):
    xml_file = MockCGIFieldStorage("test_xml_file.xml",
                                   BytesIO(test_xml_file.encode('utf-8')))
    error_msg = 'Invalid XML Content'
    mocked_post_article.side_effect = \
        managers.exceptions.ManagerFileError(
            message=error_msg
        )
    dummy_request.POST = {
        'article_id': xml_file.filename,
        'xml_file': xml_file
    }

    article_api = ArticleAPI(dummy_request)
    with pytest.raises(HTTPBadRequest) as excinfo:
        article_api.collection_post()
    assert excinfo.value.message == error_msg


@patch.object(managers, 'post_article')
def test_post_article_internal_error(mocked_post_article,
                                     dummy_request,
                                     test_xml_file):
    xml_file = MockCGIFieldStorage("test_xml_file.xml",
                                   BytesIO(test_xml_file.encode('utf-8')))
    error_msg = 'Error Catalog Manager: {}'.format(123456)
    mocked_post_article.side_effect = \
        managers.article_manager.ArticleManagerException(
            message=error_msg
        )
    dummy_request.POST = {
        'article_id': xml_file.filename,
        'xml_file': xml_file
    }

    article_api = ArticleAPI(dummy_request)
    with pytest.raises(HTTPInternalServerError) as excinfo:
        article_api.collection_post()
    assert excinfo.value.message == error_msg


@patch.object(managers, '_get_article_manager')
def test_post_article_returns_article_version_url(mocked__get_article_manager,
                                                  inmemory_article_manager,
                                                  dummy_request,
                                                  test_xml_file):
    mocked__get_article_manager.return_value = inmemory_article_manager
    inmemory_db_settings = '/rawfile'
    xml_file = MockCGIFieldStorage("test_xml_file.xml",
                                   BytesIO(test_xml_file.encode('utf-8')))
    dummy_request.POST = {
        'article_id': xml_file.filename,
        'xml_file': xml_file
    }
    article_api = ArticleAPI(dummy_request)
    response = article_api.collection_post()

    assert response.status_code == 201
    assert response.json is not None
    assert response.json.get('url').endswith(xml_file.filename)
    assert response.json.get('url').startswith(inmemory_db_settings)


@patch.object(managers, 'get_article_document')
def test_http_get_article_manifest_db_failed(
        mocked_get_article_document,
        dummy_request):
    mocked_get_article_document.side_effect = DBFailed
    dummy_request.matchdict = {'id': 'x'}
    article_manifest_api = ArticleManifest(dummy_request)
    with pytest.raises(HTTPServiceUnavailable):
        article_manifest_api.get()


@patch.object(managers, 'get_article_document')
def test_http_get_article_manifest_not_found(
        mocked_get_article_document,
        dummy_request):
    mocked_get_article_document.side_effect = \
        managers.article_manager.ArticleManagerException('')
    dummy_request.matchdict = {'id': 'x'}
    article_manifest_api = ArticleManifest(dummy_request)
    with pytest.raises(HTTPNotFound):
        article_manifest_api.get()


@patch.object(managers, 'get_article_document')
def test_http_get_article_manifest_succeeded(
        mocked_get_article_document,
        dummy_request):
    article_id = 'ID123456'
    expected = {
      "id": "0034-8910-rsp-48-2-0275",
      "versions": [
        {"data":
         "/rawfiles/0034-8910-rsp-48-2-0275/0034-8910-rsp-48-2-0275.xml",
         "assets": [
           {"0034-8910-rsp-48-2-0275-gf01.gif": [
                "/rawfiles/0034-8910-rsp-48-2-0275/"
                "0034-8910-rsp-48-2-0275-gf01.gif"
                ]}
            ]
         }
      ]
    }
    article_document = ArticleDocument(article_id)
    article_document.manifest = expected

    mocked_get_article_document.return_value = article_document

    dummy_request.matchdict = {'id': article_id}

    article_api = ArticleManifest(dummy_request)

    response = article_api.get()
    assert response.status == '200 OK'
    assert response.json == expected
