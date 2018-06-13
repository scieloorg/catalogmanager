from datetime import datetime
from random import randint

from pyramid import testing
import pytest

from persistence.databases import (
    QueryOperator,
    CouchDBManager,
    InMemoryDBManager,
)

from persistence.services import (
    DatabaseService,
    ChangesService,
    SortOrder
)
from persistence.seqnum_generator import SeqNumGenerator


@pytest.yield_fixture
def persistence_config(request):
    yield testing.setUp()
    testing.tearDown()


@pytest.fixture
def fake_change_list():
    return ['Test1', 'Test2', 'Test3', 'Test4', 'Test5', 'Test6']


@pytest.fixture
def article_db_settings():
    return {
        'database_uri': 'http://localhost:5984',
        'database_username': 'admin',
        'database_password': 'password',
        'database_name': 'articles',
    }


@pytest.fixture
def change_db_settings():
    return {
        'database_uri': 'http://localhost:5984',
        'database_username': 'admin',
        'database_password': 'password',
        'database_name': 'changes',
    }


@pytest.fixture
def seqnum_db_settings():
    return {
        'database_uri': 'http://localhost:5984',
        'database_username': 'admin',
        'database_password': 'password',
        'database_name': 'seqnum',
    }


@pytest.fixture(params=[
    CouchDBManager,
    InMemoryDBManager
])
def seqnumber_generator(request, seqnum_db_settings):
    s = SeqNumGenerator(
        request.param(**seqnum_db_settings),
        'CHANGE'
    )

    def fin():
        s.db_manager.drop_database()

    request.addfinalizer(fin)
    return s


@pytest.fixture(
    params=[
        CouchDBManager,
        InMemoryDBManager
    ]
)
def database_service(request,
                     article_db_settings,
                     change_db_settings,
                     seqnum_db_settings):
    DBManager = request.param
    s = SeqNumGenerator(
        DBManager(**seqnum_db_settings),
        'CHANGE'
    )
    db_service = DatabaseService(
        DBManager(**article_db_settings),
        ChangesService(
            DBManager(**change_db_settings),
            s
        )
    )

    def fin():
        try:
            db_service.db_manager.drop_database()
            db_service.changes_service.changes_db_manager.drop_database()
            s.db_manager.drop_database()
        except Exception:
            pass

    request.addfinalizer(fin)
    return db_service


@pytest.fixture
def inmemory_db_setup(request, persistence_config, change_db_settings):
    inmemory_db_service = DatabaseService(
        InMemoryDBManager(database_name='articles'),
        ChangesService(
            InMemoryDBManager(database_name='changes'),
            SeqNumGenerator(
                InMemoryDBManager(database_name='seqnum'),
                'CHANGE'
            )
        )
    )

    def fin():
        try:
            inmemory_db_service.db_manager.drop_database()
            inmemory_db_service.changes_service.changes_db_manager.\
                drop_database()
            inmemory_db_service.changes_service.db_manager.drop_database()
        except Exception:
            pass
    request.addfinalizer(fin)
    return inmemory_db_service


@pytest.fixture(params=[CouchDBManager, InMemoryDBManager])
def db_manager_test(request, article_db_settings):
    return request.param(**article_db_settings)


@pytest.fixture
def test_changes_records(request):
    changes_list = []
    for sequential in range(1, 11):
        document_type = ['C', 'U', 'D']
        change_record = {
            'change_id': '{:0>17}'.format(sequential),
            'document_id': 'DOC-ID-{}'.format(sequential),
            'type': document_type[randint(0, 2)],
            'created_date': str(datetime.utcnow().timestamp())
        }
        changes_list.append(change_record)
    return changes_list


@pytest.fixture
def test_documents_records(request):
    fields_values = ('{:0>17}', 'field_{}')
    return tuple(
        {
            'document_id': fields_values[0].format(sequential),
            'field': fields_values[1].format(sequential)
        }
        for sequential in range(1, 11)
    )


@pytest.fixture
def no_filter_all(request, test_documents_records):
    return (
        {'filter': {}, 'fields': [], 'sort': []},
        test_documents_records
    )


@pytest.fixture
def filter_greater_than_result(request, test_documents_records):
    initial_id = '{:0>17}'.format(5)
    find_criteria = {
        'filter': {
            'document_id': [
                (QueryOperator.GREATER_THAN, initial_id)
            ]
        },
        'fields': ['document_id', 'field'],
        'limit': 10,
        'sort': []
    }
    expected = tuple(
        {
            field: document_record[field]
            for field in ['document_id', 'field']
        }
        for document_record in test_documents_records
        if initial_id < document_record['document_id']
    )
    return (find_criteria, expected)


@pytest.fixture
def filter_limit_result(request, test_documents_records):
    limit_id = '{:0>17}'.format(5)
    find_criteria = {
        'filter': {},
        'fields': ['document_id', 'field'],
        'limit': 5,
        'sort': []
    }
    expected = tuple(
        {
            field: document_record[field]
            for field in ['document_id', 'field']
        }
        for document_record in test_documents_records
        if document_record['document_id'] <= limit_id
    )
    return (find_criteria, expected)


@pytest.fixture
def filter_greater_than_orded_by_result(request, test_documents_records):
    initial_id = '{:0>17}'.format(5)
    find_criteria = {
        'filter': {
            'document_id': [
                (QueryOperator.GREATER_THAN, initial_id)
            ]
        },
        'fields': ['document_id', 'field'],
        'limit': 10,
        'sort': [{'document_id': SortOrder.ASC.value}]
    }
    expected = tuple(
        {
            field: document_record[field]
            for field in ['document_id', 'field']
        }
        for document_record in test_documents_records
        if document_record['document_id'] > initial_id
    )
    return (find_criteria, expected)


@pytest.fixture
def filter_orded_by_result(request, test_documents_records):
    find_criteria = {
        'filter': {},
        'fields': ['document_id', 'field'],
        'limit': 10,
        'sort': [{'document_id': SortOrder.ASC.value}]
    }
    expected = tuple(
        {
            field: document_record[field]
            for field in ['document_id', 'field']
        }
        for document_record in test_documents_records
    )
    return (find_criteria, expected)


@pytest.fixture
def filter_orded_by_desc_result(request, test_documents_records):
    find_criteria = {
        'filter': {},
        'fields': ['document_id', 'field'],
        'limit': 10,
        'sort': [{'document_id': SortOrder.DESC.value}]
    }
    expected = tuple(
        {
            field: document_record[field]
            for field in ['document_id', 'field']
        }
        for document_record in test_documents_records[::-1]
    )
    return (find_criteria, expected)


@pytest.fixture(params=[
        pytest.lazy_fixture('no_filter_all'),
        pytest.lazy_fixture('filter_greater_than_result'),
        pytest.lazy_fixture('filter_limit_result'),
        pytest.lazy_fixture('filter_greater_than_orded_by_result'),
        pytest.lazy_fixture('filter_orded_by_result'),
        pytest.lazy_fixture('filter_orded_by_desc_result'),
    ]
)
def find_criteria_result(request):
    return request.param


@pytest.fixture
def xml_test():
    return """
    <?xml version = "1.0" encoding = "UTF-8"?>
    <!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.0 20120330//EN" "JATS-journalpublishing1.dtd" >
    <article xmlns: xlink = "http://www.w3.org/1999/xlink"
             xmlns: mml = "http://www.w3.org/1998/Math/MathML"
             dtd - version = "1.0"
             article - type = "research-article"
             xml: lang = "en" >
        <front>
            <journal-meta>
                <journal-id journal-id-type="nlm-ta">
                    Rev Saude Publica
                </journal-id>
                <journal-title-group>
                    <journal-title>Revista de Saúde Pública</journal-title>
                </journal-title-group>
                <issn pub-type="ppub">0034-8910</issn>
                <issn pub-type="epub">1518-8787</issn>
                <publisher>
                    <publisher-name>
                        Faculdade de Saúde Pública da Universidade de São Paulo
                    </publisher-name>
                </publisher>
            </journal-meta>
            <article-meta>
                <article-id pub-id-type="publisher-id">
                    S0034-8910.2014048004911
                </article-id>
                <article-id pub-id-type="doi">
                    10.1590/S0034-8910.2014048004911
                </article-id>
                <article-categories>
                    <subj-group subj-group-type="heading">
                        <subject>Artigos Originais</subject>
                    </subj-group>
                </article-categories>
                <title-group>
                    <article-title xml:lang="en">HIV/AIDS knowledge among men who have sex with men: applying the item response theory</article-title>
                    <trans-title-group xml:lang="pt">
                        <trans-title>Conhecimento de HIV/Aids entre homens que fazem sexo com homens: teoria de resposta ao item</trans-title>
                    </trans-title-group>
                </title-group>
                <aff id="aff1">
                    <label>I</label>
                    <institution content-type="orgname">Secretaria Municipal de Saúde de Belo Horizonte</institution>
                    <addr-line>
                        <named-content content-type="city">Belo Horizonte</named-content>
                        <named-content content-type="state">MG</named-content>
                    </addr-line>
                    <country>Brasil</country>
                    <institution content-type="original">Secretaria Municipal de Saúde de Belo Horizonte. Belo Horizonte, MG, Brasil</institution>
                </aff>
                <aff id="aff2">
                    <label>II</label>
                    <institution content-type="orgdiv1">Faculdade de Medicina</institution>
                    <institution content-type="orgname">Universidade Federal de Minas Gerais</institution>
                    <addr-line>
                        <named-content content-type="city">Belo Horizonte</named-content>
                        <named-content content-type="state">MG</named-content>
                    </addr-line>
                    <country>Brasil</country>
                    <institution content-type="original"> Grupo de Pesquisas em Epidemiologia e Avaliação em Saúde. Faculdade de Medicina. Universidade Federal de Minas Gerais. Belo Horizonte, MG, Brasil</institution>
                </aff>
                <aff id="aff3">
                    <label>III</label>
                    <institution content-type="orgdiv1">Faculdade de Educação</institution>
                    <institution content-type="orgname">Universidade Federal de Minas Gerais</institution>
                    <addr-line>
                        <named-content content-type="city">Belo Horizonte</named-content>
                        <named-content content-type="state">MG</named-content>
                    </addr-line>
                    <country>Brasil</country>
                    <institution content-type="original">Grupo de Avaliação e Medidas Educacionais. Faculdade de Educação. Universidade Federal de Minas Gerais. Belo Horizonte, MG, Brasil</institution>
                </aff>
                <aff id="aff4">
                    <label>IV</label>
                    <institution content-type="orgdiv2">Departamento de Farmácia Social</institution>
                    <institution content-type="orgdiv1">Faculdade de Farmácia</institution>
                    <institution content-type="orgname">Universidade Federal de Minas Gerais</institution>
                    <addr-line>
                        <named-content content-type="city">Belo Horizonte</named-content>
                        <named-content content-type="state">MG</named-content>
                    </addr-line>
                    <country>Brasil</country>
                    <institution content-type="original">Departamento de Farmácia Social. Faculdade de Farmácia. Universidade Federal de Minas Gerais. Belo Horizonte, MG, Brasil</institution>
                </aff>
                <aff id="aff5">
                    <label>V</label>
                    <institution content-type="orgdiv2">Departamento de Saúde Comunitária</institution>
                    <institution content-type="orgdiv1">Faculdade de Medicina</institution>
                    <institution content-type="orgname">Universidade Federal do Ceará</institution>
                    <addr-line>
                        <named-content content-type="city">Fortaleza</named-content>
                        <named-content content-type="state">CE</named-content>
                    </addr-line>
                    <country>Brasil</country>
                    <institution content-type="original">Departamento de Saúde Comunitária. Faculdade de Medicina. Universidade Federal do Ceará. Fortaleza, CE, Brasil</institution>
                </aff>
                <aff id="aff6">
                    <label>VI</label>
                    <institution content-type="orgdiv2">Departamento de Medicina Preventiva e Social</institution>
                    <institution content-type="orgdiv1">Faculdade de Medicina</institution>
                    <institution content-type="orgname">Universidade Federal de Minas Gerais</institution>
                    <addr-line>
                        <named-content content-type="city">Belo Horizonte</named-content>
                        <named-content content-type="state">MG</named-content>
                    </addr-line>
                    <country>Brasil</country>
                    <institution content-type="original">Departamento de Medicina Preventiva e Social. Faculdade de Medicina. Universidade Federal de Minas Gerais. Belo Horizonte, MG, Brasil</institution>
                </aff>
                <author-notes>
                    <corresp>
                        <label>Correspondence</label>:  Raquel Regina de Freitas Magalhães Gomes  Rua Virgílio Uchoa, 627 Belo Horizonte  30320-240 Belo Horizonte, MG, Brasil  E-mail: <email>quelfmg@gmail.com</email>
                    </corresp>
                    <fn fn-type="other">
                        <p>This article was based on the doctorate thesis of Gomes RRFM, entitled: “Conhecimento sobre HIV/Aids entre homens que fazem sexo com homens em dez cidades brasileiras”, presented to the <italic>Universidade Federal de Minas Gerais</italic>, in 2014.</p>
                    </fn>
                    <fn fn-type="conflict">
                        <p>The authors declare that there is no conflict of interest.</p>
                    </fn>
                </author-notes>
                <pub-date pub-type="epub-ppub">
                    <month>04</month>
                    <year>2014</year>
                </pub-date>
                <volume>48</volume>
                <issue>2</issue>
                <fpage>206</fpage>
                <lpage>215</lpage>
                <history>
                    <date date-type="received">
                        <day>24</day>
                        <month>4</month>
                        <year>2013</year>
                    </date>
                    <date date-type="accepted">
                        <day>12</day>
                        <month>11</month>
                        <year>2013</year>
                    </date>
                </history>
                <permissions>
                    <license license-type="open-access"
                             xlink:href="http://creativecommons.org/licenses/by-nc/3.0/">
                        <license-p>This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License, which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.</license-p>
                    </license>
                </permissions>
            </article-meta>
        </front>
        <body>
            <sec sec-type="intro">
                <title>INTRODUCTION</title>
                <p>Test</p>
            </sec>
            <sec sec-type="methods">
                <title>METHODS</title>
                <p>Test</p>
            </sec>
            <sec sec-type="results">
                <title>RESULTS</title>
                <p>Test</p>
            </sec>
        </body>
    </article>
    """
