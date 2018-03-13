# coding=utf-8

from . import article_record


class ArticleReception:

    def __init__(self, data_storage):
        self.data_storage = data_storage

    def asset_data_record_items(self, article, article_id):
        asset_record = article_record.AssetRecord()
        article.link_files_to_assets()
        if article.assets is not None:
            return {name: asset_record.input(asset, article_id) for name, asset in article.assets.items()}

    def save_asset_records(self, asset_records):
        if asset_records is not None:
            saved = {}
            for name, record in asset_records.items():
                save_id = self.data_storage.save(record)
                saved[name] = save_id
            return saved

    def save_article(self, article, article_id):
        if article.assets is not None:
            article.link_files_to_assets()
            asset_records = self.asset_data_record_items()
            asset_id_items = self.save_asset_records(asset_records)
            article.update_href(asset_id_items)

        a_record = article_record.ArticleRecord()
        record = a_record.input(
            article, article_id, asset_id_items)
        return self.data_storage.save(record)
