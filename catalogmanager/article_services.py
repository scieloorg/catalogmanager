# coding=utf-8
from catalog_persistence.models import (
        get_record,
        RecordType,
    )
from catalog_persistence.databases import (
        DatabaseService,
    )
from .data_services import DataServices
from .models.article_model import (
    Article,
    File
)


Record = get_record


def FileProperties(file):
    return {
        'content_size': file.size,
        'content_type': file.content_type,
        'file_fullpath': file.file_fullpath,
        'file_name': file.name,
        'file_path': file.path,
    }


class ArticleServices:

    def __init__(self, articles_db_manager, changes_db_manager):
        self.article_data_services = DataServices('articles')
        self.article_db_service = DatabaseService(
            articles_db_manager, changes_db_manager)

    def receive_article(self, id, xml, files):
        article = Article(xml, files)
        article.id = id
        article_record = Record(
            document_id=article.id,
            content=article.get_record_content(),
            document_type=RecordType.ARTICLE)

        self.article_db_service.register(
            article.id, article_record)

        f = File(article.xml_tree.file_fullpath)
        self.article_db_service.put_attachment(
                document_id=article.id,
                file_id=f.name,
                content=f.content,
                file_properties=FileProperties(f)
            )

        if article.assets is not None:
            for name, asset in article.assets.items():
                self.article_db_service.put_attachment(
                        document_id=article.id,
                        file_id=asset.file.name,
                        content=asset.file.content,
                        file_properties=FileProperties(asset.file)
                    )
        return self.article_db_service.read(article.id)

    def get_article_file(self, article_url):
        article_id = self.article_data_services.get_article_id(article_url)
        article_record = self.article_db_service.read(article_id)
        return self.article_db_service.get_attachment(
            document_id=article_id,
            file_id=article_record['content']['xml_name']
        )
