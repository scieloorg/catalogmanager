from catalogmanager.article_services import ArticleServices
from catalog_persistence.databases import CouchDBManager, InMemoryDBManager


def get_article_file(article_url, db_host, db_port, username, password):
    database_config = {
        'couchdb.uri': '{}:{}'.format(db_host, db_port),
        'couchdb.username': username,
        'couchdb.password': password,
    }
    articles_database_config = database_config.copy()
    articles_database_config['database_name'] = "articles"
    changes_database_config = database_config.copy()
    changes_database_config['database_name'] = "changes"

    article_services = ArticleServices(
        CouchDBManager(articles_database_config),
        CouchDBManager(changes_database_config)
    )
    return article_services.get_article(article_url)
