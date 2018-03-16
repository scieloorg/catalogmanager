import pytest
import os

from catalogmanager.models import article_model
from catalogmanager.receptions import article_reception
from catalogmanager.datastorages import article_storage
from catalogmanager.datastorages import data_storage


def get_files():
    xml_filename = './packages/0034-8910-rsp-S01518-87872016050006741/0034-8910-rsp-S01518-87872016050006741.xml'
    files = [item for item in os.listdir('./packages/0034-8910-rsp-S01518-87872016050006741/') if not item.endswith('.xml')]
    return (xml_filename, files)


def create_article(xml_filename, files):
    return article_model.Article(xml_filename, files)


def test_article_reception():
    xml_filename, files = get_files()
    article = create_article(xml_filename, files)

    ds = data_storage.DataStorage()
    article_ds = article_storage.ArticleStorage(ds)
    asset_ds = article_storage.AssetStorage(ds)

    reception = article_reception.ArticleReception(article_ds, asset_ds)
    location = '{}/articles/{}'.format('APP_URI', '123')
    assert location == reception.register_article(article, '123')
