from managers.article_manager import ArticleManager
from managers.exceptions import ManagerFileError
from managers.models.article_model import ArticleDocument, InvalidXMLContent
from managers.models.file import File
from persistence.databases import CouchDBManager
from persistence.services import (
    DatabaseService,
    ChangesService,
)
from persistence.seqnum_generator import SeqNumGenerator


def _get_changes_dbmanager(database_config_copy):
    changes_database_config = database_config_copy
    changes_database_config['database_name'] = "changes"
    return CouchDBManager(**changes_database_config)


def _get_changes_services(db_settings):
    database_config = db_settings

    changes_seqnum_database_config = database_config.copy()
    changes_seqnum_database_config['database_name'] = "changes_seqnum"

    return ChangesService(
        _get_changes_dbmanager(database_config.copy()),
        SeqNumGenerator(
            CouchDBManager(**changes_seqnum_database_config),
            'CHANGES_SEQ'
        )
    )


def _get_article_manager(**db_settings):
    articles_database_config = db_settings.copy()
    articles_database_config['database_name'] = "articles"
    files_database_config = db_settings.copy()
    files_database_config['database_name'] = "files"

    return ArticleManager(
        CouchDBManager(**articles_database_config),
        CouchDBManager(**files_database_config),
        _get_changes_services(db_settings)
    )


def create_file(filename, content):
    """
    Cria instancia de objeto File que será usado para o tratamento dos
    dados do documento a ser persistido

    Params:
    filename: nome do arquivo a ser manipulado
    content: conteúdo do arquivo

    Return:
    Objeto File, que deverá ser informado nas funções do managers
    """
    return File(file_name=filename, content=content)


def post_article(article_id, xml_id, xml_file, **db_settings):
    """
    Registra novo documento de artigo em banco de dados informado, persistindo
    a versão codificada em XML recebida e um manifesto do artigo contendo a
    referência para recuperar o arquivo XML.

    :param article_id: ID do Documento do tipo Artigo, para identificação
        referencial
    :param xml_id: identificação do arquivo
    :param xml_file: objeto File-like conteúdo do XML
    :param db_settings: dicionário com as configurações do banco de dados.
        Deve conter:
        - database_uri: URI do banco de dados (host:porta)
        - database_username: usuário do banco de dados
        - database_password: senha do banco de dados

    :returns: URL pública para recuperar a versão registrada do artigo
        codificado em XML
    :rtype: str
    """
    article_document = ArticleDocument(article_id)
    article_manager = _get_article_manager(**db_settings)
    try:
        article_document.add_version(xml_id, xml_file)
    except InvalidXMLContent as e:
        raise ManagerFileError(message=e.message)
    else:
        return article_manager.add_document(article_document)


def put_article(article_id, xml_file, assets_files=[], **db_settings):
    """
    Registra Documento de Artigo, com XML e seus ativos digitais e cria
    metadados para controle de integridade referencial

    :param article_id: ID do Documento do tipo Artigo, para identificação
        referencial
    :param xml_file: objeto File com nome e conteúdo do XML
    :param assets_files: lista de objetos File contendo os arquivos dos
        ativos digitais do Artigo, cada um com nome e seu respectivo
        conteúdo
    :param db_settings: dicionário com as configurações do banco de dados.
        Deve conter:
        - database_uri: URI do banco de dados (host:porta)
        - database_username: usuário do banco de dados
        - database_password: senha do banco de dados

    :returns: lista com os nomes dos arquivos de ativos digitais não
        referenciados no XML e lista com os nomes dos arquivos de ativos
        digitais referenciados no XML e que não constam na lista de
        arquivos de ativos digitais informada
    :rtype: tuple(list(), list())
    """
    article_manager = _get_article_manager(**db_settings)
    return article_manager.receive_package(id=article_id,
                                           xml_file=xml_file,
                                           files=assets_files)


def get_article_data(article_id, **db_settings):
    """
    Recupera metadados do Documento de Artigo, usados para controle de
    integridade referencial

    :param article_id: ID do Documento do tipo Artigo, para identificação
        referencial
    :param db_settings: dicionário com as configurações do banco de dados.
        Deve conter:
        - database_uri: URI do banco de dados (host:porta)
        - database_username: usuário do banco de dados
        - database_password: senha do banco de dados

    :returns: dicionário com os metadados
    """
    article_manager = _get_article_manager(**db_settings)
    return article_manager.get_article_data(article_id)


def get_article_document(article_id, **db_settings):
    """
    Recupera metadados do Documento de Artigo, usados para controle de
    integridade referencial

    :param article_id: ID do Documento do tipo Artigo, para identificação
        referencial
    :param db_settings: dicionário com as configurações do banco de dados.
        Deve conter:
        - database_uri: URI do banco de dados (host:porta)
        - database_username: usuário do banco de dados
        - database_password: senha do banco de dados

    :returns: dicionário com os metadados
    """
    article_manager = _get_article_manager(**db_settings)
    return article_manager.get_article_document(article_id)


def get_article_file(article_id, **db_settings):
    """
    Recupera Arquivo XML do Artigo

    :param article_id: ID do Documento do tipo Artigo, para identificação
        referencial
    :param db_settings: dicionário com as configurações do banco de dados.
        Deve conter:
        - database_uri: URI do banco de dados (host:porta)
        - database_username: usuário do banco de dados
        - database_password: senha do banco de dados

    :returns: Arquivo XML do Artigo
    """
    article_manager = _get_article_manager(**db_settings)
    return article_manager.get_article_file(article_id)


def get_asset_file(article_id, asset_id, **db_settings):
    """
    Recupera Ativo Digital do Artigo

    :param article_id: ID do Documento do tipo Artigo, para identificação
        referencial
    :param asset_id: nome de identificação do ativo digital
    :param db_settings: dicionário com as configurações do banco de dados.
        Deve conter:
        - database_uri: URI do banco de dados (host:porta)
        - database_username: usuário do banco de dados
        - database_password: senha do banco de dados

    :returns: Arquivo de Ativo digital
    """
    article_manager = _get_article_manager(**db_settings)
    return article_manager.get_asset_file(article_id, asset_id)


def set_assets_public_url(article_id, xml_content, assets_filenames,
                          public_url):
    """
    Atualiza hrefs dos ativos digitais com a URL pública no conteúdo do
    XML informado, tornando-os acessíveis via interface da API

    :param article_id: ID do Documento do tipo Artigo, para identificação
        referencial
    :param xml_content: conteúdo XML a ser atualizado
    :param assets_filenames: nome de identificação dos ativos digitais
        contidos no XML
    :param public_url: base da URL pública a ser colocada nos hrefs

    :returns: conteúdo do XML atualizado
    """
    xml_file = File(file_name="xml_file.xml", content=xml_content)
    article = ArticleDocument(article_id)
    article.xml_file = xml_file
    for name in article.assets:
        if name in assets_filenames:
            article.assets[name].href = public_url.format(article_id,
                                                          name)
    return article.xml_tree.content


def list_changes(last_sequence, limit, **db_settings):
    """
    Retorna lista de todas as mudanças a partir de sequencial informado,
    na ordem em que ocorreram, limitadas ao parâmetro de limite informado.

    :param last_sequence: sequencial de mudança, que deve ser a referência
        para a busca dos sequenciais a serem listados.
    :param limit: limite máximo de registros de mudança que devem ser
        listados.
    :param db_settings: dicionário com as configurações do banco de dados.
        Deve conter:
        - database_uri: URI do banco de dados (host:porta)
        - database_username: usuário do banco de dados
        - database_password: senha do banco de dados

    :returns: lista de mundanças
    :rtype: list()
    """
    change_service = DatabaseService(
        None,
        _get_changes_services(db_settings.copy())
    )
    return change_service.list_changes(last_sequence=last_sequence,
                                       limit=limit)
