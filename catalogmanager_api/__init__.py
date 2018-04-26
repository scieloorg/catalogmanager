
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from pyramid.paster import get_appsettings
from pyramid.response import Response
from pyramid.view import view_config, notfound_view_config


@view_config(route_name='home')
def home(request):
    return Response('')


@notfound_view_config()
def notfound(request):
    return HTTPNotFound(body='{"message": "Not found"}')


def includeme(config):
    config.include("cornice")
    config.scan("catalogmanager_api.views")


def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.include(includeme)
    config.add_route('home', '/')

    def couchdb_settings(request):
        ini_settings = get_appsettings(global_config['__file__'])
        return {
            'database_uri': '{}:{}'.format(
                ini_settings['catalogmanager.db.host'],
                ini_settings['catalogmanager.db.port']
            ),
            'database_username': ini_settings['catalogmanager.db.username'],
            'database_password': ini_settings['catalogmanager.db.password']
        }

    config.add_request_method(couchdb_settings, 'db_settings', reify=True)

    config.scan()
    return config.make_wsgi_app()
