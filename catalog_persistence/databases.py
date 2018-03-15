from collections import namedtuple
from datetime import datetime
import abc

import couchdb


class DocumentNotFound(Exception):
    pass


class BaseDBManager(metaclass=abc.ABCMeta):

    database_names = {
        'A': 'articles',
        'D': 'assets'
    }

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


class InMemoryDBManager(BaseDBManager):

    def __init__(self, database_name):
        self._db_name = database_name
        self._database = {}

    @property
    def database(self):
        table = self._database.get(self._db_name)
        if not table:
            self._database[self._db_name] = {}
        return self._database[self._db_name]

    def drop_database(self):
        self._database = {}

    def create(self, document):
        doc = {}
        for key, value in document.items():
            if type(value) == str:
                doc.update({key: value})
            elif type(value) == datetime:
                doc.update({key: str(value.timestamp())})
        self.database.update({document['_id']: doc})
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


class CouchDBManager(BaseDBManager):

    def __init__(self, settings):
        self._db_name = settings['database_name']
        self._database = None
        self._db_server = couchdb.Server(settings['couchdb.uri'])
        self._db_server.resource.credentials = (
            settings['couchdb.username'],
            settings['couchdb.password']
        )

    @property
    def database(self):
        try:
            self._database = self._db_server[self._db_name]
        except couchdb.http.ResourceNotFound:
            self._database = self._db_server.create(self._db_name)
        return self._database

    def drop_database(self):
        if self._db_name:
            self._db_server.delete(self._db_name)

    def create(self, document):
        doc = {}
        for key, value in document.items():
            if type(value) == str:
                doc.update({key: value})
            elif type(value) == datetime:
                doc.update({key: str(value.timestamp())})

        id, rev = self.database.save(doc)
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


class DatabaseService():

    def __init__(self, collection):
        self.collection = collection

    def register(self, document):
        return self.collection.create(document)

    def read(self, id):
        return self.collection.read(id)

    def update(self, document):
        return self.collection.update(document)

    def delete(self, id):
        self.collection.delete(id)

    def list(self):
        return self.collection.list()
