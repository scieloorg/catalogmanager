import io
from pathlib import Path

from pyramid.httpexceptions import (
        HTTPCreated,
        HTTPNotFound,
        HTTPInternalServerError,
        HTTPServiceUnavailable,
        )
from pyramid.response import Response
from cornice.resource import resource

import managers


@resource(collection_path='/articles', path='/articles/{id}', renderer='json',
          tags=['articles'])
class Article:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    def _get_file_property(self, file_field):
        file_path = Path(file_field.filename)
        content = file_field.file.read()
        return managers.create_file(filename=file_path.name,
                                    content=content)

    def put(self):
        """Receive Article document package which must contain a XML file and
        assets files referenced."""
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
            managers.put_article(
                article_id=self.request.matchdict['id'],
                xml_file=xml_file,
                assets_files=assets_files,
                **self.request.db_settings
            )
        except managers.article_manager.ArticleManagerException as e:
            #XXX a exceção tratada aqui está sinalizando uma miríade de
            #situações excepcionais, que abarca erro de dado fornecido pelo
            #usuário, erro no servidor, e recursos não encontrados.
            raise HTTPInternalServerError(detail=e.message)
        else:
            raise HTTPCreated()

    def get(self):
        """Returns Article document metadata."""
        try:
            article_data = managers.get_article_data(
                article_id=self.request.matchdict['id'],
                **self.request.db_settings
            )
            return article_data
        except managers.article_manager.ArticleManagerException as e:
            raise HTTPNotFound(detail=e.message)


@resource(path='/articles/{id}/_manifest', renderer='json')
class ArticleManifest:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    def get(self):
        """Returns Article document manifest."""
        try:
            article_data = managers.get_article_data(
                article_id=self.request.matchdict['id'],
                **self.request.db_settings
            )
            return article_data
        except managers.article_manager.ArticleManagerException as e:
            raise HTTPNotFound(detail=e.message)
        except:
            raise HTTPServiceUnavailable()


@resource(path='/articles/{id}/xml', renderer='xml')
class ArticleXML:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    def get(self):
        """Returns XML Article file with updated public URLs to its assets."""
        try:
            article_id = self.request.matchdict['id']
            xml_file_content = managers.get_article_file(
                article_id=article_id,
                **self.request.db_settings
            )
            article_data = managers.get_article_data(
                article_id=article_id,
                **self.request.db_settings
            )
            if article_data['content'].get('assets'):
                xml_file_content = managers.set_assets_public_url(
                    article_id=article_id,
                    xml_content=xml_file_content,
                    assets_filenames=article_data['content']['assets'],
                    public_url='/articles/{}/assets/{}'
                )
            return Response(content_type='application/xml',
                            body_file=io.BytesIO(xml_file_content))
        except managers.article_manager.ArticleManagerException as e:
            raise HTTPNotFound(detail=e.message)


@resource(path='/articles/{id}/assets/{asset_id}')
class ArticleAsset:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    def get(self):
        """Returns Asset file."""
        try:
            content_type, content = managers.get_asset_file(
                article_id=self.request.matchdict['id'],
                asset_id=self.request.matchdict['asset_id'],
                **self.request.db_settings
            )
            return Response(content_type=content_type, body=content)
        except managers.article_manager.ArticleManagerException as e:
            raise HTTPNotFound(detail=e.message)
