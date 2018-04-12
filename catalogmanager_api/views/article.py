import json

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

    def put(self):
        try:
            file = self.request.POST.get('xml_file')
            catalogmanager.put_article(
                article_id=self.request.matchdict['id'],
                xml_file=file.filename,
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
                self.request.matchdict['id'],
                **self.db_settings
            )
            return json.dumps(article_data)
        except catalogmanager.article_services.ArticleServicesException as e:
            return json.dumps({
                "error": "404",
                "message": "Article not found"
            })
