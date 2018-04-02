# coding=utf-8

import os

from catalog_persistence.models import (
        get_record,
        RecordType,
    )
from catalog_persistence.databases import (
        DatabaseService,
    )
from .data_services import DataServices
from .models.article_model import Article


Record = get_record


class ArticleServices:

    def __init__(self, articles_db_manager, changes_db_manager):
        self.article_data_services = DataServices('articles')
        self.article_db_service = DatabaseService(
            articles_db_manager, changes_db_manager)

    def receive_article(self, xml, files):
        article = Article(xml, files)
        article_record = Record(
            document_id=article.id,
            content=article.get_record_content(),
            document_type=RecordType.ARTICLE)

        self.article_db_service.register(
            article.id, article_record)

        self.article_db_service.put_attachment(
                document_id=article.id,
                file_id=article.xml_tree.basename,
                content=article.xml_tree.bytes_content,
                content_type='text/xml',
                content_size=0
            )

        if files is not None:
            for f in files:
                with open(f, 'rb') as fb:
                    self.article_db_service.put_attachment(
                        document_id=article.id,
                        file_id=os.path.basename(f),
                        content=fb.read(),
                        content_type='image/png',
                        content_size=0
                    )
        return self.article_data_services.location(article.id)

    def get_article_data(self, article_id):
        article_record = self.article_db_service.read(article_id)
        return article_record

    def get_article(self, article_url):
        article_id = self.article_data_services.get_article_id(article_url)
        article_record = self.article_db_service.read(article_id)
        return self.article_db_service.get_attachment(
            document_id=article_id,
            file_id=article_record['content']['xml_name']
        )
