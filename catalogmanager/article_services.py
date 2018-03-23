# coding=utf-8

from catalog_persistence.models import (
        Record,
        RecordType,
    )
from catalog_persistence.databases import (
        DatabaseService,
    )
from .data_services import DataServices
from .models.article_model import Article


class ReceivedArticle:

    def __init__(self, xml, files):
        self.article = Article(xml, files)
        self.article.link_files_to_assets()

    @property
    def asset_records(self):
        items = {}
        for name, asset in self.article.assets.items():
            asset.article_id = self.article_record.document_id
            items[asset.name] = Record(asset.get_content(), RecordType.ASSET)
        return items

    @property
    def article_record(self):
        return Record(self.article.get_content(), RecordType.ARTICLE)

    def update_assets_location(self, assets_locations):
        self.article.update_href(assets_locations)


class ArticleServices:

    def __init__(self, articles_db_manager, assets_db_manager, changes_db_manager):
        self.article_services = DataServices('articles')
        self.asset_services = DataServices('assets')
        self.article_db_services = DatabaseService(
            articles_db_manager, changes_db_manager)
        self.asset_db_services = DatabaseService(
            assets_db_manager, changes_db_manager)

    def receive(self, xml_filename, files):
        received = ReceivedArticle(xml_filename, files)

        locations = {}
        for name, record in received.asset_records.items():
            asset_id = self.asset_db_services.register(
                record.document_id, record.serialize())
            locations[name] = self.asset_services.location(asset_id)
        received.update_assets_location(locations)

        article_record = received.article_record
        id = self.article_db_services.register(
            article_record.document_id, article_record.serialize())
        received.article.location = self.article_services.location(id)
        return received
