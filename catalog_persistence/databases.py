import abc
from datetime import datetime

import couchdb


class DocumentNotFound(Exception):
    pass


class BaseDBManager(metaclass=abc.ABCMeta):

    database_names = {
        'A': 'articles',
        'D': 'assets'
    }

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

    @abc.abstractmethod
    def register_change(self, document) -> None:
        return NotImplemented


class InMemoryDBManager(BaseDBManager):

    def __init__(self, config):
        self._changes_database = config
        self._db_name = None
        self._database = {}

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
        self.database.update({document['_id']: document})
        return document['_id']

    def read(self, id):
        doc = self.database.get(id)
        if not doc:
            raise DocumentNotFound
        return doc

    def update(self, document):
        self.database[document['_id']] = document
        return document['_id']

    def delete(self, id):
        del self.database[id]

    def find(self):
        return [
            document
            for id, document
            in self.database.items()
        ]

    def register_change(self, change):
        self.database = self._changes_database
        self.database.update(change)
        self.database = self._db_name


class CouchDBManager(BaseDBManager):

    def __init__(self, settings):
        self._db_name = None
        self._database = None
        self._changes_database = settings['couchdb.changes_database']
        self._db_server = couchdb.Server(settings['couchdb.uri'])
        self._db_server.resource.credentials = (
            settings['couchdb.username'],
            settings['couchdb.password']
        )

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
        document.update({
            'created_date': datetime.utcnow().timestamp()
        })
        id, rev = self.database.save(document)
        return id

    def read(self, id):
        try:
            doc = self.database[id]
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        return dict(doc)

    def update(self, document):
        self.database[document['_id']] = document
        return document['_id']

    def delete(self, id):
        doc = self.database[id]
        self.database.delete(doc)

    def find(self):
        mango = {
            'selector': {'type': 'A'}
        }
        return [
            document
            for document in self.database.find(mango)
        ]

    def register_change(self, change):
        self.database = self._changes_database
        self.database.save(change)
        self.database = self._db_name


class DatabaseService:

    def __init__(self, collection, database_name):
        self.collection = collection
        self.collection.database = database_name

    def register(self, document):
        document_id = self.collection.create(document)
        self.collection.register_change({
            'document_type': document['document_type'],
            'type': 'C',
            'created_date': datetime.utcnow().timestamp()
        })
        return document_id

    def read(self, id):
        return self.collection.read(id)

    def update(self, document):
        return self.collection.update(document)

    def delete(self, id):
        self.collection.delete(id)

    def find(self):
        return self.collection.find()
