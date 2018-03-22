import os

from catalog_persistence.databases import (
    InMemoryDBManager,
)

from catalogmanager.receptions.article_reception import(
    ArticleReception,
)


def get_files():
    xml_filename = './packages/0034-8910-rsp-S01518-87872016050006741/0034-8910-rsp-S01518-87872016050006741.xml'
    files = [item for item in os.listdir('./packages/0034-8910-rsp-S01518-87872016050006741/') if not item.endswith('.xml')]
    return (xml_filename, files)


def test_article_reception():
    xml_filename, files = get_files()

    changes_db_manager = InMemoryDBManager({'database_name': 'changes'})
    articles_db_manager = InMemoryDBManager({'database_name': 'articles'})
    assets_db_manager = InMemoryDBManager({'database_name': 'assets'})

    reception = ArticleReception(articles_db_manager, assets_db_manager, changes_db_manager)
    received = reception.receive(xml_filename, files)
    assert received.article.location == reception.article_services.location(received.article_record.document_id)
