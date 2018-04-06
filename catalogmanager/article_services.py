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

    def receive_package(self, id, xml_file_path, files=None):
        article = self.receive_xml_file(id, xml_file_path)
        self.receive_asset_files(article, files)
        return article.unexpected_files_list, article.missing_files_list

    def receive_xml_file(self, id, xml_file_path):
        article = Article(id)

        article.xml_file = xml_file_path

        article_record = Record(
            document_id=article.id,
            content=article.get_record_content(),
            document_type=RecordType.ARTICLE)

        self.article_db_service.register(
            article.id, article_record)

        self.article_db_service.put_attachment(
            document_id=article.id,
            file_id=article.xml_file.name,
            content=article.xml_tree.content,
            file_properties=FileProperties(article.xml_file)
        )
        return article

    def receive_asset_files(self, article, files):
        if files is not None:
            for file in files:
                self.receive_asset_file(article, file)

    def receive_asset_file(self, article, file):
        if file is not None:
            asset = article.update_asset_file(file)
            if asset is not None:
                self.article_db_service.put_attachment(
                    document_id=article.id,
                    file_id=asset.file.name,
                    content=asset.file.content,
                    file_properties=FileProperties(asset.file)
                )
