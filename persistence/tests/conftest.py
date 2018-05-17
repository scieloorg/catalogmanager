from pyramid import testing
import pytest

from persistence.databases import (
    CouchDBManager,
    InMemoryDBManager,
)
from persistence.services import DatabaseService


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


@pytest.fixture(params=[
    CouchDBManager,
    InMemoryDBManager
])
def database_service(request, article_db_settings, change_db_settings):
    return DatabaseService(
        request.param(**article_db_settings),
        request.param(**change_db_settings)
    )


@pytest.fixture
def setup(request, persistence_config, database_service):
    def fin():
        database_service.db_manager.drop_database()
        database_service.changes_db_manager.drop_database()
    request.addfinalizer(fin)


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
