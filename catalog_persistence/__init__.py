#!/usr/bin/python
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config


db_server = None


@view_config()
def hello_world(request):
    return Response('Hello!')


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.scan()
    return config.make_wsgi_app()
