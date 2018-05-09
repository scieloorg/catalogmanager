import io
from pathlib import Path

from pyramid.httpexceptions import (
        HTTPCreated,
        HTTPNotFound,
        HTTPInternalServerError,
        )
from pyramid.response import Response
from cornice.resource import resource

import catalogmanager


@resource(collection_path='/articles', path='/articles/{id}', renderer='json')
class Article:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    def _get_file_property(self, file_field):
        file_path = Path(file_field.filename)
        content = file_field.file.read()
        return catalogmanager.create_file(filename=file_path.name,
                                          content=content)

    def put(self):
        try:
            xml_file_field = self.request.POST.get('xml_file')
            xml_file = self._get_file_property(xml_file_field)

            assets_files_field = self.request.POST.getall('asset_field')
            assets_files = [
                self._get_file_property(asset_file_field)
                for asset_file_field in assets_files_field
            ]
            #XXX não há uma maneira de saber se trata-se da criação de um
            #novo recurso ou da atualização de um já existente para
            #a emissão correta dos códigos HTTP -- 201 e 200, respectivamente.
            catalogmanager.put_article(
                article_id=self.request.matchdict['id'],
                xml_file=xml_file,
                assets_files=assets_files,
                **self.request.db_settings
            )
        except catalogmanager.article_services.ArticleServicesException as e:
            #XXX a exceção tratada aqui está sinalizando uma miríade de
            #situações excepcionais, que abarca erro de dado fornecido pelo
            #usuário, erro no servidor, e recursos não encontrados.
            raise HTTPInternalServerError(detail=e.message)
        else:
            raise HTTPCreated()

    def get(self):
        try:
            article_data = catalogmanager.get_article_data(
                article_id=self.request.matchdict['id'],
                **self.request.db_settings
            )
            return article_data
        except catalogmanager.article_services.ArticleServicesException as e:
            raise HTTPNotFound(detail=e.message)


@resource(path='/articles/{id}/xml', renderer='json')
class ArticleXML:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    def get(self):
        try:
            article_id = self.request.matchdict['id']
            xml_file_content = catalogmanager.get_article_file(
                article_id=article_id,
                **self.request.db_settings
            )
            article_data = catalogmanager.get_article_data(
                article_id=article_id,
                **self.request.db_settings
            )
            if article_data['content'].get('assets'):
                xml_file_content = catalogmanager.set_assets_public_url(
                    article_id=article_id,
                    xml_content=xml_file_content,
                    assets_filenames=article_data['content']['assets'],
                    public_url='/articles/{}/assets/{}'
                )
            return Response(content_type='application/xml',
                            body_file=io.BytesIO(xml_file_content))
        except catalogmanager.article_services.ArticleServicesException as e:
            raise HTTPNotFound(detail=e.message)


@resource(path='/articles/{id}/assets/{asset_id}', renderer='json')
class ArticleAsset:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    def get(self):
        try:
            content_type, content = catalogmanager.get_asset_file(
                article_id=self.request.matchdict['id'],
                asset_id=self.request.matchdict['asset_id'],
                **self.request.db_settings
            )
            return Response(content_type=content_type, body=content)
        except catalogmanager.article_services.ArticleServicesException as e:
            raise HTTPNotFound(detail=e.message)
