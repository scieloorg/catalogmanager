
from pyramid.config import Configurator
from pyramid.paster import get_appsettings
from pyramid.response import Response
from pyramid.view import view_config, notfound_view_config


@view_config(route_name='home')
def home(request):
    return Response('')


@notfound_view_config()
def notfound(request):
    return Response(
        body='{"message": "Not found"}',
        status='404 Not Found'
    )


def includeme(config):
    config.include("cornice")
    config.scan("catalogmanager_api.views")


def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.include(includeme)
    config.add_route('home', '/')
    config.add_route('get_xml', '/articles/{id}/xml')

    ini_settings = get_appsettings(global_config['ini_filename'])
    config.registry.settings['database_host'] = \
        ini_settings['catalogmanager.db.host']
    config.registry.settings['database_port'] = \
        ini_settings['catalogmanager.db.port']
    config.registry.settings['database_username'] = \
        ini_settings['catalogmanager.db.username']
    config.registry.settings['database_password'] = \
        ini_settings['catalogmanager.db.password']

    config.scan()
    return config.make_wsgi_app()
