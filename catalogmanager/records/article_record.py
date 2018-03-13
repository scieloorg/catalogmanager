# coding=utf-8

from ..models import article_data


class AssetRecord:

    def __init__(self):
        pass

    def input(self, asset, article_id):
        record = {}
        record['basename'] = asset.basename
        record['filename'] = asset.filename
        record['file'] = asset.file
        record['node'] = asset.asset_node
        record['article_id'] = article_id
        return record

    def output(self, record):
        return article_data.Asset(record.get('filename'), record.get('node'))


class ArticleRecord:

    def __init__(self):
        pass

    def input(self, article, article_id, asset_id_items):
        record = {}
        record['filename'] = article.filename
        record['basename'] = article.basename
        record['content'] = article.xml_tree.content
        record['assets'] = asset_id_items
        record['article_id'] = article_id
        return record

    def output(self, record):
        return article_data.Article(record.get('file'), record.get('files'))
