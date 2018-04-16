import json
from collections import OrderedDict
from unittest.mock import patch

import webtest
import catalogmanager


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
    mocked_get_article_data.side_effect = \
        catalogmanager.article_services.ArticleServicesException(
            message='Missing XML file {}'.format(article_id)
        )
    expected = {
        "error": "404",
        "message": "Article not found"
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
        xml_properties={
            'filename': "test_xml_file.xml",
            'content': test_xml_file.encode('utf-8'),
            'content_size': len(test_xml_file)
        },
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
