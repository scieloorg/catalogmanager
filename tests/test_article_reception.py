import os

from catalog_persistence.databases import (
    InMemoryDBManager,
)
from catalog_persistence.models import (
    RecordType,
)

from catalogmanager.article_services import(
    ArticleServices,
)


def get_files():
    xml_filename = './packages/0034-8910-rsp-S01518-87872016050006741/0034-8910-rsp-S01518-87872016050006741.xml'
    files = [item for item in os.listdir('./packages/0034-8910-rsp-S01518-87872016050006741/') if not item.endswith('.xml')]
    return (xml_filename, files)


def test_article_reception():
    xml_filename, files = get_files()

    expected = {
        'document_id': '336abebdd31894idnaoexistente',
        'document_type': RecordType.ARTICLE.value,
        'content': {'Test': 'Test4'},
        'created_date': '01010101'
    }

    article = Article(xml, files)
    article_record = expected
    
        db_service.register(
            article.id, article_record)
        db_service.register_attachment(
            document_id=article.id,
            attach_name=article.xml_tree.basename,
            content=article.xml_tree.filename
            )
        if files is not None:
            for f in files:
                db_service.register_attachment(
                    document_id=article.id,
                    attach_name=os.path.basename(f),
                    content=f
                    )
        return self.article_data_services.location(article.id)

    changes_db_manager = InMemoryDBManager({'database_name': 'changes'})
    articles_db_manager = InMemoryDBManager({'database_name': 'articles'})

    article_services = ArticleServices(
        articles_db_manager, changes_db_manager)
    gotten = article_services.receive(xml_filename, files)
    assert expected == gotten







