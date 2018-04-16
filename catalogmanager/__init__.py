from catalogmanager.article_services import (
    ArticleServices
)
from catalog_persistence.databases import CouchDBManager


def _get_article_service(db_host, db_port, username, password):
    database_config = {
        'database_uri': '{}:{}'.format(db_host, db_port),
        'database_username': username,
        'database_password': password,
    }
    articles_database_config = database_config.copy()
    articles_database_config['database_name'] = "articles"
    changes_database_config = database_config.copy()
    changes_database_config['database_name'] = "changes"

    return ArticleServices(
        CouchDBManager(**articles_database_config),
        CouchDBManager(**changes_database_config)
    )


def put_article(article_id, xml_properties, assets_files=None, **kwargs):
    article_services = _get_article_service(kwargs['db_host'],
                                            kwargs['db_port'],
                                            kwargs['username'],
                                            kwargs['password'])
    return article_services.receive_package(id=article_id,
                                            files=assets_files,
                                            **xml_properties)


def get_article_data(article_id, db_host, db_port, username, password):
    article_services = _get_article_service(db_host,
                                            db_port,
                                            username,
                                            password)
    return article_services.get_article_data(article_id)


def get_article_file(article_id, db_host, db_port, username, password):
    article_services = _get_article_service(db_host,
                                            db_port,
                                            username,
                                            password)
    return article_services.get_article_file(article_id)
