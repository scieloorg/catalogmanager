# coding=utf-8
import hashlib
from enum import Enum

from ..xml.article_xml_tree import ArticleXMLTree


class InvalidXMLContent(Exception):
    message = "Invalid XML Content"


class DocumentType(Enum):
    DOCUMENT = 'DOC'
    ARTICLE = 'ART'


class AssetDocument:
    """Metadados de um documento do tipo Ativo Digital.
    Um Ativo Digital é um arquivo associado a um documento do tipo Artigo
    por meio de uma referência interna na estrutura da sua representação em
    XML.

    ``asset_node`` deve ser uma instância de
    :class:`managers.xml.article_xml_tree.HRefNode`.
    """
    def __init__(self, asset_node):
        #XXX :attr:`.file` vaza encapsulamento, i.e., seu estado não é
        #gerenciado pela instância mas pelo seu cliente.
        self.file = None
        self.node = asset_node
        self.name = asset_node.href

    @property
    def href(self):
        """Acessa ou define a URI do ativo digital na referência interna da
        representação XML do Artigo.
        """
        if self.node is not None:
            return self.node.href

    @href.setter
    def href(self, value):
        if self.node is not None:
            self.node.href = value


class ArticleDocument:
    """Metadados de um documento do tipo Artigo."""
    def __init__(self, article_id):
        self.id = article_id
        self.versions = []
        self.assets = {}
        self.unexpected_files_list = []

    def add_version(self, file_id, xml_content):
        """Adiciona nova versão de artigo codificado em XML em :attr:`versions`
        e cria nova referência para atualizar os dados do manifesto do artigo.
        Caso o conteúdo do XML for inválido, a exceção
        :class:`InvalidXMLContent` é lançada.
        """
        self.xml_tree = ArticleXMLTree(xml_content)
        if self.xml_tree.xml_error:
            raise InvalidXMLContent
        checksum = hashlib.sha1(xml_content).hexdigest()
        self.xml_file_id = '/'.join([checksum[:13], file_id])
        self.versions.append({
            'data': self.xml_file_id,
            'assets': []
        })

    def update_version(self, added_file_url):
        """
        Atualiza referência do artigo codificado em XML em :attr:`versions`.
        """
        self.versions[-1].update({'data': added_file_url})

    @property
    def xml_file(self):
        """Acessa ou define o documento Artigo em XML, representado por uma
        instância de :class:`managers.models.file.File`. A definição de
        um novo documento Artigo resultará na identificação dos seus ativos,
        i.e., o valor do atributo :attr:`.assets` será modificado.

        Adicionalmente, a definição de um novo documento Artigo causará a
        definição do atributo :attr:`.xml_tree`.

        O acesso ao documento Artigo antes que este seja inicializado resultará
        na exceção :class:`AttributeError`.
        """
        return self._xml_file

    @xml_file.setter
    def xml_file(self, xml_file):
        self._xml_file = xml_file
        self.xml_tree = ArticleXMLTree(xml_file.content)
        if self.xml_tree.xml_error:
            raise InvalidXMLContent
        self.assets = {
            name: AssetDocument(node)
            for name, node in self.xml_tree.asset_nodes.items()
        }

    def update_asset_files(self, files):
        """Associa a sequência de ativos ``files`` aos metadados de um Artigo,
        sobrescrevendo valores associados anteriormente.

        Retorna uma lista com os nomes dos arquivos associados com sucesso.
        """
        updated = []
        if files is not None:
            for file in files:
                updated.append(self.update_asset_file(file))
        return updated

    def update_asset_file(self, file):
        """Associa o ativo ``file`` aos metadados de um Artigo, sobrescrevendo
        valores associados anteriormente.

        Retorna instância de :class:`AssetDocument` no caso de sucesso, ou
        ``None`` caso contrário. Caso o valor retornado seja ``None`` você
        poderá inspecionar o atributo :attr:`.unexpected_files_list` para
        saber se trata-se de um ativo desconhecido pelo Artigo ou se trata-se
        de um artigo que não possui o atributo ``name``.
        """
        name = file.name
        if name:
            if name in self.assets.keys():
                self.assets[name].file = file
                return self.assets[name]
            self.unexpected_files_list.append(name)

    def get_record_content(self):
        """Obtém um dicionário que descreve a instância de
        :class:`ArticleDocument` da seguinte maneira: chave ``xml``, contendo o
        nome do arquivo associado a :attr:`.xml_file` e chave ``assets``,
        contendo os nome dos arquivos dos ativos digitais associados ao Artigo.
        """
        record_content = {}
        record_content['xml'] = self.xml_file.name
        record_content['assets'] = [
            asset.name
            for asset in self.assets.values()
        ]
        return record_content

    def get_record(self):
        """Obtém um dicionário que descreve a instância de
        :class:`ArticleDocument` da seguinte maneira: chave ``id``, contendo o
        ID do artigo e chave ``versions``, contendo uma lista de versões do
        artigo, com a URI da respectiva codificação XML e seus assets.
        """
        record_content = {}
        record_content['document_id'] = self.id
        record_content['document_type'] = DocumentType.ARTICLE.value
        record_content['versions'] = self.versions
        return record_content

    @property
    def missing_files_list(self):
        """Obtém uma lista com os nomes dos arquivos dos ativos digitais do
        Artigo que estão faltando.
        """
        return [
            name
            for name, asset in self.assets.items()
            if asset.file is None
        ]
