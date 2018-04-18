import json
from collections import OrderedDict
from unittest.mock import patch

import webtest
import catalogmanager


def _get_file_property(filename, content, size):
    return {
        'filename': filename,
        'content': content,
        'content_size': size
    }


def test_http_get_home(testapp):
    result = testapp.get('/', status=200)
    assert result.status == '200 OK'
    assert result.body == b''


@patch.object(catalogmanager, 'get_article_data')
def test_http_get_article_calls_get_article_data(mocked_get_article_data,
                                                 db_settings,
                                                 testapp):
    article_id = 'ID123456'
    mocked_get_article_data.return_value = {"test": "123"}
    testapp.get('/articles/{}'.format(article_id))
    mocked_get_article_data.assert_called_once_with(
        article_id=article_id,
        **db_settings
    )


@patch.object(catalogmanager, 'get_article_data')
def test_http_get_article_not_found(mocked_get_article_data, testapp):
    article_id = 'ID123456'
    error_msg = 'Article {} not found'.format(article_id)
    mocked_get_article_data.side_effect = \
        catalogmanager.article_services.ArticleServicesException(
            message=error_msg
        )
    expected = {
        "error": "404",
        "message": error_msg
    }
    result = testapp.get('/articles/{}'.format(article_id))
    assert result.status == '200 OK'
    assert result.json == json.dumps(expected)


@patch.object(catalogmanager, 'get_article_data')
def test_http_get_article_succeeded(mocked_get_article_data, testapp):
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
    result = testapp.get('/articles/{}'.format(article_id))
    assert result.status == '200 OK'
    assert result.json == json.dumps(expected)


@patch.object(catalogmanager, 'get_article_file')
def test_http_get_xml_file_calls_get_article_file(mocked_get_article_file,
                                                  db_settings,
                                                  testapp):
    article_id = 'ID123456'
    mocked_get_article_file.return_value = b'123456Test'
    testapp.get('/articles/{}/xml'.format(article_id))
    mocked_get_article_file.assert_called_once_with(
        article_id=article_id,
        **db_settings
    )


@patch.object(catalogmanager, 'get_article_file')
def test_http_get_xml_file_article_not_found(mocked_get_article_file, testapp):
    article_id = 'ID123456'
    error_msg = 'Article {} not found'.format(article_id)
    mocked_get_article_file.side_effect = \
        catalogmanager.article_services.ArticleServicesException(
            message=error_msg
        )
    expected = {
        "error": "404",
        "message": error_msg
    }
    result = testapp.get('/articles/{}/xml'.format(article_id))
    assert result.status == '200 OK'
    assert result.json == expected


@patch.object(catalogmanager, 'get_article_file')
def test_http_get_xml_file_not_found(mocked_get_article_file, testapp):
    article_id = 'ID123456'
    error_msg = 'Missing XML file {}'.format(article_id)
    mocked_get_article_file.side_effect = \
        catalogmanager.article_services.ArticleServicesException(
            message=error_msg
        )
    expected = {
        "error": "404",
        "message": error_msg
    }
    result = testapp.get('/articles/{}/xml'.format(article_id))
    assert result.status == '200 OK'
    assert result.json == expected


@patch.object(catalogmanager, 'get_article_file')
def test_http_get_xml_file_succeeded(mocked_get_article_file,
                                     testapp, test_xml_file):
    article_id = 'ID123456'
    expected = test_xml_file.encode('utf-8')
    mocked_get_article_file.return_value = expected
    result = testapp.get('/articles/{}/xml'.format(article_id))
    assert result.status == '200 OK'
    assert result.body == expected
    assert result.content_type == 'application/xml'


@patch.object(catalogmanager, 'put_article')
def test_http_article_calls_put_article(mocked_put_article,
                                        db_settings,
                                        testapp,
                                        test_xml_file):
    article_id = 'ID-post-article-123'
    params = OrderedDict([
        ('article_id', article_id),
        ("xml_file",
         webtest.forms.Upload("test_xml_file.xml",
                              test_xml_file.encode('utf-8')))
    ])
    testapp.put('/articles/{}'.format(article_id),
                params=params,
                content_type='multipart/form-data')
    mocked_put_article.assert_called_once_with(
        article_id=article_id,
        xml_properties=_get_file_property("test_xml_file.xml",
                                          test_xml_file.encode('utf-8'),
                                          len(test_xml_file)),
        assets_files=[],
        **db_settings
    )


@patch.object(catalogmanager, 'put_article')
def test_http_article_calls_put_article_service_error(mocked_put_article,
                                                      testapp,
                                                      test_xml_file):
    article_id = 'ID-post-article-123'
    mocked_put_article.side_effect = \
        catalogmanager.article_services.ArticleServicesException(
            message='Missing XML file {}'.format(article_id)
        )
    expected = {
        "error": "500",
        "message": "Article error"
    }
    params = OrderedDict([
        ('article_id', article_id),
        ("xml_file",
         webtest.forms.Upload("test_xml_file.xml",
                              test_xml_file.encode('utf-8')))
    ])
    result = testapp.put('/articles/{}'.format(article_id),
                         params=params,
                         content_type='multipart/form-data')
    assert result.status == '200 OK'
    assert result.json == json.dumps(expected)


@patch.object(catalogmanager, 'put_article')
def test_http_article_put_article_succeeded(mocked_put_article,
                                            testapp,
                                            test_xml_file):
    article_id = 'ID-post-article-123'
    params = OrderedDict([
        ('article_id', article_id),
        ("xml_file",
         webtest.forms.Upload("test_xml_file.xml",
                              test_xml_file.encode('utf-8')))
    ])
    result = testapp.put('/articles/{}'.format(article_id),
                         params=params,
                         content_type='multipart/form-data')
    assert result.status == '200 OK'


@patch.object(catalogmanager, 'put_article')
def test_http_article_put_article_with_assets(mocked_put_article,
                                              db_settings,
                                              testapp,
                                              test_xml_file,
                                              test_article_files):
    article_id = 'ID-post-article-123'
    expected_assets_properties = []
    assets_field = []
    for article_file in test_article_files:
        with open(article_file, 'rb') as fb:
            file_content = fb.read()
            expected_assets_properties.append(
                _get_file_property(article_file.name,
                                   file_content,
                                   article_file.lstat().st_size),
            )
        assets_field.append(
            ('asset_field', article_file.name, file_content)
        )
    params = OrderedDict([
        ('article_id', article_id),
        ("xml_file",
         webtest.forms.Upload("test_xml_file.xml",
                              test_xml_file.encode('utf-8')))
    ])
    result = testapp.put('/articles/{}'.format(article_id),
                         params=params,
                         upload_files=assets_field,
                         content_type='multipart/form-data')
    assert result.status == '200 OK'
    mocked_put_article.assert_called_once_with(
        article_id=article_id,
        xml_properties=_get_file_property("test_xml_file.xml",
                                          test_xml_file.encode('utf-8'),
                                          len(test_xml_file)),
        assets_files=expected_assets_properties,
        **db_settings
    )
