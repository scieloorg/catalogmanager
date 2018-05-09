# coding=utf-8

from ..xml.article_xml_tree import ArticleXMLTree


class AssetDocument:
    """Metadados de um documento do tipo Ativo Digital.
    
    Um Ativo Digital é um arquivo associado a um documento do tipo Artigo
    por meio de uma referência interna na estrutura da sua representação em
    XML.

    ``asset_node`` deve ser uma instância de
    :class:`catalogmanager.xml.article_xml_tree.HRefNode`.
    """
    def __init__(self, asset_node):
        #XXX :attr:`.file` vaza encapsulamento, i.e., seu estado não é
        #gerenciado pela instância mas pelo seu cliente.
        self.file = None
        self.node = asset_node
        #XXX :attr:`.name` e :attr:`.href` perdem integridade após atribuição
        #em :attr:`.href`.
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
    """Metadados de um documento do tipo Artigo.

    Os metadados contam com uma referência ao Artigo codificado em XML e 
    referências aos seus ativos digitais.

    Exemplo de uso:

        #XXX note que a inicialização da instância não é feita por completo no
        #momento devido.

        >>> doc = ArticleDocument('art01')
        >>> doc.xml_file = <instância de File>  
    """
    def __init__(self, article_id):
        self.id = article_id
        self.assets = {}
        self.unexpected_files_list = []

    @property
    def xml_file(self):
        """Acessa ou define o documento Artigo em XML, representado por uma
        instância de :class:`catalogmanager.models.file.File`. A definição de
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
        #XXX o atributo não é definido até que :meth:`xml_file` seja 
        #executado definindo um documento Artigo, i.e., a API do objeto
        #varia de acordo com o seu ciclo de vida.
        self.xml_tree = ArticleXMLTree()   
        self.xml_tree.content = self._xml_file.content
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
