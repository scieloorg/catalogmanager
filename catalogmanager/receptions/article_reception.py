# coding=utf-8

from ..records import article_record


class ArticleReception:

    def __init__(self, data_storage):
        self.data_storage = data_storage

    def register_asset_records(self, asset_records):
        if asset_records is not None:
            registered = {}
            for name, record in asset_records.items():
                registered_id = self.data_storage.register(record)
                registered[name] = registered_id
            return registered

    def register_article(self, article, article_id):
        a_record = article_record.ArticleRecord()
        if article.assets is not None:
            article.link_files_to_assets()
            asset_records = a_record.asset_data_record_items()
            asset_id_items = self.register_asset_records(asset_records)
            article.update_href(asset_id_items)
        record = a_record.input(
            article, article_id, asset_id_items)
        return self.data_storage.register(record)
