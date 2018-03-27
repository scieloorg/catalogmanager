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

        self.article_db_service.register_attachment(
                document_id=article.id,
                attach_name=article.xml_tree.basename,
                content=article.xml_tree.filename
            )

        if files is not None:
            for f in files:
                self.article_db_service.register_attachment(
                        document_id=article.id,
                        attach_name=os.path.basename(f),
                        content=f
                    )
        return self.article_data_services.location(article.id)
