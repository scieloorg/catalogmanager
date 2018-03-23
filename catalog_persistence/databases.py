import abc
from datetime import datetime
from enum import Enum
from uuid import uuid4

import couchdb


class DocumentNotFound(Exception):
    pass


class ChangeType(Enum):
    CREATE = 'C'
    UPDATE = 'U'
    DELETE = 'D'


class BaseDBManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def drop_database(self) -> None:
        return NotImplemented

    @abc.abstractmethod
    def create(self, id, document) -> str:
        return NotImplemented

    @abc.abstractmethod
    def read(self, id) -> dict:
        return NotImplemented

    @abc.abstractmethod
    def update(self, id, document) -> str:
        return NotImplemented

    @abc.abstractmethod
    def delete(self, id) -> None:
        return NotImplemented

    @abc.abstractmethod
    def find(self) -> list:
        return NotImplemented


class InMemoryDBManager(BaseDBManager):

    def __init__(self, config):
        self.database_name = config['database_name']
        self._database = {}

    @property
    def database(self):
        table = self._database.get(self.database_name)
        if not table:
            self._database[self.database_name] = {}
        return self._database[self.database_name]

    def drop_database(self):
        self._database = {}

    def create(self, id, document):
        self.database.update({id: document})
        return id

    def read(self, id):
        doc = self.database.get(id)
        if not doc:
            raise DocumentNotFound
        return doc

    def update(self, id, document):
        self.database.update({id: document})
        return id

    def delete(self, id):
        doc = self.database.get(id)
        if not doc:
            raise DocumentNotFound
        del self.database[id]

    def find(self):
        return [document for id, document in self.database.items()]


class CouchDBManager(BaseDBManager):

    def __init__(self, settings):
        self.database_name = settings['database_name']
        self._database = None
        self._db_server = couchdb.Server(settings['couchdb.uri'])
        self._db_server.resource.credentials = (
            settings['couchdb.username'],
            settings['couchdb.password']
        )

    @property
    def database(self):
        try:
            self._database = self._db_server[self.database_name]
        except couchdb.http.ResourceNotFound:
            self._database = self._db_server.create(self.database_name)
        return self._database

    def drop_database(self):
        if self.database_name:
            try:
                self._db_server.delete(self.database_name)
            except couchdb.http.ResourceNotFound:
                pass

    def create(self, id, document):
        self.database[id] = document
        return id

    def read(self, id):
        try:
            doc = dict(self.database[id])
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        return doc

    def update(self, id, document):
        try:
            """
            Para atualizar documento no CouchDB, é necessário informar a
            revisão do documento atual. Por isso, é obtido o documento atual
            para que os dados dele sejam atualizados com o registro informado.
            """
            doc = dict(self.database[id])
            doc.update(document)
            self.database[id] = doc
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        return id

    def delete(self, id):
        try:
            doc = self.database[id]
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        self.database.delete(doc)

    def find(self):
        mango = {
            'selector': {'document_type': 'ART'}
        }
        return [dict(document) for document in self.database.find(mango)]


class DatabaseService:
    """
    Database Service é responsável por persistir registros de documentos(dicts)
    em um DBManager e de mudanças relacionadas a eles em outro DBManager, ambos
    informados na instanciação desta classe.

    db_manager: Instância do DBManager para persistir registro de documentos
    changes_db_manager: Instância do DBManager para persistir registro de
        mudanças
    """

    def __init__(self, db_manager, changes_db_manager):
        self.db_manager = db_manager
        self.changes_db_manager = changes_db_manager

    def _register_change(self, document_record, change_type):
        change_record = {
            'change_id': uuid4().hex,
            'document_id': document_record['document_id'],
            'document_type': document_record['document_type'],
            'type': change_type.value,
            'created_date': str(datetime.utcnow().timestamp()),
        }
        change_id = self.changes_db_manager.create(
            change_record['change_id'],
            change_record
        )
        return change_id

    def register(self, document_id, document_record):
        """
        Persiste registro de um documento e a mudança na base de dados.

        Params:
        document_id: ID do documento
        document_record: registro do documento

        Retorno:
        ID do documento
        """
        document_record.update({
            'created_date': str(datetime.utcnow().timestamp())
        })
        document_id = self.db_manager.create(document_id, document_record)
        self._register_change(document_record, ChangeType.CREATE)
        return document_id

    def read(self, document_id):
        """
        Obtém registro de um documento pelo ID do documento na base de dados.

        Params:
        document_id: ID do documento

        Retorno:
        registro de documento registrado na base de dados

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
        """
        return self.db_manager.read(document_id)

    def update(self, document_id, document_record):
        """
        Atualiza o registro de um documento e a mudança na base de dados.

        Params:
        document_id: ID do documento a ser atualizado
        document_record: registro de documento a ser atualizado

        Retorno:
        ID do documento atualizado

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
        """
        document_record.update({
            'updated_date': str(datetime.utcnow().timestamp())
        })
        document_id = self.db_manager.update(document_id, document_record)
        self._register_change(document_record, ChangeType.UPDATE)
        return document_id

    def delete(self, document_id, document_record):
        """
        Remove registro de um documento e a mudança na base de dados.

        Params:
        document_id: ID do documento a ser deletado
        document_record: registro de documento a ser deletado

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
        """
        self.db_manager.delete(document_id)
        self._register_change(document_record, ChangeType.DELETE)

    def find(self):
        """
        Busca registros de documento pelo ID do documento na base de dados.

        Retorno:
        Lista de registros de documento registrado na base de dados
        """
        return self.db_manager.find()
