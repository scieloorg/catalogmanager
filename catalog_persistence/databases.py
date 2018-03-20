import abc
from datetime import datetime
from enum import Enum
from uuid import uuid4

import couchdb

from catalog_persistence.models import DocumentRecord


class DocumentNotFound(Exception):
    pass


class ChangeType(Enum):
    CREATE = 'C'
    UPDATE = 'U'
    DELETE = 'D'


class Change:

    def __init__(self, document_record, change_type):
        self._record_id = uuid4().hex
        self._document_id = document_record.document_id
        self._document_type = document_record.document_type.value
        self._type = change_type.value

    @property
    def document_id(self):
        return self._record_id

    @document_id.setter
    def document_id(self, record_id):
        self._record_id = record_id

    @property
    def created_date(self):
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        self._created_date = created_date

    def input(self):
        return {
            'record_id': self.document_id,
            'document_id': self._document_id,
            'document_type': self._document_type,
            'type': self._type,
            'created_date': self.created_date,
        }

    def output(self):
        return {}


class BaseDBManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def database(self, database_name) -> None:
        return NotImplemented

    @abc.abstractmethod
    def drop_database(self) -> None:
        return NotImplemented

    @abc.abstractmethod
    def create(self, document) -> str:
        return NotImplemented

    @abc.abstractmethod
    def read(self, id) -> dict:
        return NotImplemented

    @abc.abstractmethod
    def update(self, document) -> str:
        return NotImplemented

    @abc.abstractmethod
    def delete(self, id) -> None:
        return NotImplemented

    @abc.abstractmethod
    def find(self) -> list:
        return NotImplemented


class InMemoryDBManager(BaseDBManager):

    def __init__(self, config):
        self._db_name = None
        self._database = {}

    @property
    def database_name(self):
        return self._db_name

    @property
    def database(self):
        table = self._database.get(self._db_name)
        if not table:
            self._database[self._db_name] = {}
        return self._database[self._db_name]

    @database.setter
    def database(self, database_name):
        self._db_name = database_name

    def drop_database(self):
        self._database = {}

    def create(self, document):
        document.created_date = str(datetime.utcnow().timestamp())
        self.database.update({document.document_id: document.input()})
        return document.document_id

    def read(self, id):
        doc = self.database.get(id)
        if not doc:
            raise DocumentNotFound
        return doc

    def update(self, document):
        self.database.update({document.document_id: document.input()})
        return document.document_id

    def delete(self, id):
        doc = self.database.get(id)
        if not doc:
            raise DocumentNotFound
        del self.database[id]

    def find(self):
        return [document for id, document in self.database.items()]


class CouchDBManager(BaseDBManager):

    def __init__(self, settings):
        self._db_name = None
        self._database = None
        self._db_server = couchdb.Server(settings['couchdb.uri'])
        self._db_server.resource.credentials = (
            settings['couchdb.username'],
            settings['couchdb.password']
        )

    @property
    def database_name(self):
        return self._db_name

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, database_name):
        self._db_name = database_name
        try:
            self._database = self._db_server[self._db_name]
        except couchdb.http.ResourceNotFound:
            self._database = self._db_server.create(self._db_name)

    def drop_database(self):
        if self._db_name:
            self._db_server.delete(self._db_name)

    def create(self, document):
        document.created_date = str(datetime.utcnow().timestamp())
        self.database[document.document_id] = document.input()
        return document.document_id

    def read(self, id):
        try:
            doc = dict(self.database[id])
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        return doc

    def update(self, document):
        try:
            doc = self.database[document.document_id]
            self.database[doc.document_id] = document.input()
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        return document.document_id

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
    Database Service é responsável por persistir DocumentRecords no DBManager,
    ambos informados na instanciação desta classe.

    db_manager: Instância do DBManager
    database_name: Nome da base de dados para persistir DocumentRecord
    changes_database(opcional): Nome da base de dados para persistir Change
    """

    def __init__(self, db_manager, database_name, changes_database='changes'):
        self.db_manager = db_manager
        self.db_manager.database = database_name
        self.changes_database = changes_database

    def _register_change(self, document_record, change_type):
        self.db_manager.database, document_database = (
            self.changes_database,
            self.db_manager.database_name
        )
        change_record = Change(document_record, change_type)
        change_id = self.db_manager.create(change_record)
        self.db_manager.database = document_database
        return change_id

    def register(self, document_record):
        """
        Registra DocumentRecord e Change na base de dados.

        Params:
        document_record: Instância de DocumentRecord

        Retorno:
        ID do documento criado
        """
        document_id = self.db_manager.create(document_record)
        self._register_change(document_record, ChangeType.CREATE)
        return document_id

    def read(self, id):
        """
        Obtém DocumentRecord pelo ID do documento na base de dados.

        Params:
        id: ID do documento

        Retorno:
        DocumentRecord registrado na base de dados

        Erro:
        DocumentNotFound: Documento não encontrado na base de dados.
        """
        document_record = self.db_manager.read(id)
        return DocumentRecord(document_record, id).output()

    def update(self, document_record):
        """
        Atualiza DocumentRecord na base de dados.

        Params:
        document_record: DocumentRecord a ser atualizado

        Retorno:
        ID do documento atualizado

        Erro:
        DocumentNotFound: Documento não encontrado na base de dados.
        """
        document_id = self.db_manager.update(document_record)
        self._register_change(document_record, ChangeType.UPDATE)
        return document_id

    def delete(self, document_record):
        """
        Obtém DocumentRecord pelo ID do documento na base de dados.

        Params:
        id: ID do documento

        Retorno:
        DocumentRecord registrado na base de dados

        Erro:
        DocumentNotFound: Documento não encontrado na base de dados.
        """
        self.db_manager.delete(document_record.document_id)
        self._register_change(document_record, ChangeType.DELETE)

    def find(self):
        return [
            DocumentRecord(document, document['document_id']).output()
            for document in self.db_manager.find()
        ]
