# coding=utf-8

from ..models import article_model


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
        record['asset_id'] = asset.asset_node.id
        record['id'] = self.gen_id(record)
        return record

    def gen_id(self, record):
        return record.get('article_id')+'_'+record.get('asset_id')

    def output(self, record):
        return article_model.Asset(record.get('filename'), record.get('node'))


class ArticleRecord:

    def __init__(self):
        pass

    def input(self, article, article_id, asset_id_items):
        record = {}
        record['filename'] = article.filename
        record['basename'] = article.basename
        record['content'] = article.content
        record['assets'] = asset_id_items
        record['article_id'] = article_id
        record['id'] = self.gen_id(record)
        return record

    def gen_id(self, record):
        return record.get('article_id')

    def output(self, record):
        return article_model.Article(record.get('file'), record.get('files'))

    def asset_record_items(self, article, article_id):
        asset_record = AssetRecord()
        if article.assets is not None:
            return {name: asset_record.input(asset, article_id) for name, asset in article.assets.items()}
