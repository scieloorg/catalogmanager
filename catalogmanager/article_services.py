# coding=utf-8

from catalog_persistence.models import (
        get_record,
        RecordType,
    )
from catalog_persistence.databases import (
        DatabaseService,
        DocumentNotFound
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


class ArticleServicesException(Exception):

    def __init__(self, message):
        self.message = message


class ArticleServicesMissingAssetFileException(Exception):
    pass


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

    def get_article_data(self, article_id):
        try:
            article_record = self.article_db_service.read(article_id)
            return article_record
        except DocumentNotFound:
            raise ArticleServicesException(
                'Missing XML file {}'.format(article_id)
            )

    def get_article_file(self, article_id):
        article_record = self.get_article_data(article_id)
        try:
            return self.article_db_service.get_attachment(
                document_id=article_id,
                file_id=article_record['content']['xml']
            )
        except DocumentNotFound:
            raise ArticleServicesException(
                'Missing XML file {}'.format(article_id)
            )

    def get_asset_files(self, article_id):
        article_record = self.get_article_data(article_id)
        assets = article_record['content'].get('assets') or []
        asset_files = {}
        missing = []
        for file_id in assets:
            try:
                asset_files[file_id] = self.get_asset_file(article_id, file_id)
            except ArticleServicesException:
                missing.append(file_id)
        return asset_files, missing

    def get_asset_file(self, article_id, file_id):
        try:
            return self.article_db_service.get_attachment(
                document_id=article_id,
                file_id=file_id
            )
        except DocumentNotFound:
            raise ArticleServicesException(
                'Missing asset file: {}. '.format(file_id)
            )
