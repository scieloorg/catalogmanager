# coding=utf-8

from . import article as article_module


class AssetRecord:

    def __init__(self):
        pass

    def data(self, asset, article_id):
        _data = {}
        _data['basename'] = asset.basename
        _data['filename'] = asset.filename
        _data['file'] = asset.file
        _data['node'] = asset.asset_node
        _data['article_id'] = article_id
        return _data

    def object(self, data):
        return article_module.Asset(data.get('filename'), data.get('node'))


class ArticleRecord:

    def __init__(self):
        pass

    def data(self, article, article_id, asset_id_items):
        _data = {}
        _data['filename'] = article.filename
        _data['basename'] = article.basename
        _data['content'] = article.xml_tree.content
        _data['assets'] = asset_id_items
        _data['article_id'] = article_id
        return _data

    def article(self, data):
        return article_module.Article(data.get('file'), data.get('files'))


class ArticleRecord:

    def __init__(self, data_storage):
        self.data_storage = data_storage
        self.asset_record = AssetRecord(data_storage)

    def asset_data_record_items(self, article, article_id):
        article.link_files_to_assets()
        asset_record = AssetRecord()
        if article.assets is not None:
            return {name: asset_record.data(asset, article_id) for name, asset in article.assets.items()}

    def save_assets(self, data_storage, article, article_id):
        article.link_files_to_assets()
        asset_records = self.asset_data_record_items(article, article_id)
        if asset_records is not None:
            saved = {}
            for name, record in asset_records.items():
                save_id = data_storage.save(record)
                saved[name] = save_id
            return saved

    def data(self, article, article_id):
        saved = self.save_assets(data_storage, article, article_id)

        _data = {}
        _data['name'] = article.xml_filename
        _data['content'] = article.content
        _data['assets'] = asset.asset_node
        _data['article_id'] = article_id
        return _data

    def article(self, data):
        return article_module.Article(data.get('file'), data.get('files'))
