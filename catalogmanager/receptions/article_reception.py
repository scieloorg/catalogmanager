# coding=utf-8

from ..records import article_record


class ArticleReception:

    def __init__(self, article_data_storage, asset_data_storage):
        self.article_data_storage = article_data_storage
        self.asset_data_storage = asset_data_storage

    def register_asset_records(self, assets):
        if assets is not None:
            registered = {}
            for asset in assets:
                asset_record = article_record.AssetRecord(asset.get_content())
                registered_id = self.asset_data_storage.register(asset_record)
                registered[asset.name] = registered_id
            return registered

    def register_article(self, article, article_id):
        asset_id_items = None
        if article.assets is not None:
            article.link_files_to_assets()
            asset_id_items = self.register_assets(article.assets)
            article.update_href(asset_id_items)
        a_record = article_record.ArticleRecord(article.get_content())
        return self.article_data_storage.register(a_record)
