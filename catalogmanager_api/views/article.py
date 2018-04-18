import os
import json

from pyramid.response import Response
from pyramid.view import view_config
from cornice.resource import resource
import catalogmanager


@resource(collection_path='/articles', path='/articles/{id}', renderer='json')
class Article:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context
        self.settings = request.registry.settings
        self.db_settings = {
            'db_host': self.settings.get('database_host'),
            'db_port': self.settings.get('database_port'),
            'username': self.settings.get('database_username'),
            'password': self.settings.get('database_password')
        }

    def _get_file_property(self, file_field):
        content = file_field.file.read()
        size = len(content)
        return {
            'filename': os.path.basename(file_field.filename),
            'content': content,
            'content_size': size
        }

    def put(self):
        try:
            xml_file_field = self.request.POST.get('xml_file')
            xml_properties = self._get_file_property(xml_file_field)

            assets_files_field = self.request.POST.getall('asset_field')
            assets_files = [
                self._get_file_property(asset_file_field)
                for asset_file_field in assets_files_field
            ]
            catalogmanager.put_article(
                article_id=self.request.matchdict['id'],
                xml_properties=xml_properties,
                assets_files=assets_files,
                **self.db_settings
            )
        except catalogmanager.article_services.ArticleServicesException as e:
            return json.dumps({
                "error": "500",
                "message": "Article error"
            })

    def get(self):
        try:
            article_data = catalogmanager.get_article_data(
                article_id=self.request.matchdict['id'],
                **self.db_settings
            )
            return json.dumps(article_data)
        except catalogmanager.article_services.ArticleServicesException as e:
            return json.dumps({
                "error": "404",
                "message": e.message
            })

    @view_config(route_name='get_article_xml')
    def get_article_xml(self):
        try:
            xml_file = catalogmanager.get_article_file(
                article_id=self.request.matchdict['id'],
                **self.db_settings
            )
            return Response(content_type='application/xml', body=xml_file)
        except catalogmanager.article_services.ArticleServicesException as e:
            return Response(
                json={
                    "error": "404",
                    "message": e.message
                }
            )
