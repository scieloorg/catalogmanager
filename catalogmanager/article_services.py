# coding=utf-8

from catalog_persistence.models import (
        get_record,
        RecordType,
    )
from catalog_persistence.databases import DocumentNotFound
from catalog_persistence.services import DatabaseService
from .models.article_model import (
    ArticleDocument,
)
from .models.file import File


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
        self.article_db_service = DatabaseService(
            articles_db_manager, changes_db_manager)

    def receive_package(self, id, files=None, **xml_properties):
        article = self.receive_xml_file(id, **xml_properties)
        self.receive_asset_files(article, files)
        return article.unexpected_files_list, article.missing_files_list

    def receive_xml_file(self, id, **xml_properties):
        article = ArticleDocument(id)

        xml_file = File(xml_properties['filename'])
        xml_file.content = xml_properties['content']
        xml_file.size = xml_properties['content_size']
        article.xml_file = xml_file

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
            for file_properties in files:
                self.receive_asset_file(article, file_properties)

    def receive_asset_file(self, article, file_properties):
        if file_properties is not None:
            asset = article.update_asset_file(file_properties)
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
                'ArticleDocument {} not found'.format(article_id)
            )

    def get_article_file(self, article_id):
        article_record = self.get_article_data(article_id)
        article = ArticleDocument(article_id)
        try:
            attachment = self.article_db_service.get_attachment(
                document_id=article_id,
                file_id=article_record['content']['xml']
            )

            xml_file = File(article_record['content']['xml'])
            xml_file.content = attachment
            xml_file.size = len(attachment)
            article.xml_file = xml_file
            return article.xml_file.content
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

    def get_asset_file(self, article_id, asset_id):
        try:
            content = self.article_db_service.get_attachment(
                document_id=article_id,
                file_id=asset_id
            )
            properties = self.article_db_service.get_attachment_properties(
                document_id=article_id,
                file_id=asset_id
            )
            content_type = '' if properties is None else properties.get(
                'content_type',
                ''
            )
            return content_type, content
        except DocumentNotFound:
            raise ArticleServicesException(
                'AssetDocument file {} (ArticleDocument {}) not found.'.format(
                    asset_id, article_id)
            )
