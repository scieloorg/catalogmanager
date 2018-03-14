from collections import namedtuple
from datetime import datetime
import abc

import couchdb


class DocumentNotFound(Exception):
    pass


class BaseDBManager(metaclass=abc.ABCMeta):

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

    def __init__(self):
        self.data = []

    def drop_database(self):
        del self.data[:]

    def create(self, document):
        pass

    def read(self, id):
        pass

    def update(self, document):
        pass

    def delete(self, id):
        pass


class CouchDBManager(BaseDBManager):

    database_names = {
        'A': 'articles',
        'D': 'assets'
    }

    def __init__(self, settings):
        self._db_name = None
        self.__database = None
        self._db_server = couchdb.Server(settings['couchdb.uri'])
        self._db_server.resource.credentials = (
            settings['couchdb.username'],
            settings['couchdb.password']
        )

    @property
    def _database(self):
        return self.__database

    @_database.setter
    def _database(self, document_type):
        self._db_name = self.database_names[document_type]
        try:
            self.__database = self._db_server[self._db_name]
        except couchdb.http.ResourceNotFound:
            self.__database = self._db_server.create(self._db_name)

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

        self._database = document['type']
        id, rev = self._database.save(doc)
        return id

    def read(self, id):
        try:
            doc = self._database[id]
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        return dict(doc)

    def update(self, document):
        self._database[document['_id']] = document
        return document['_id']

    def delete(self, id):
        doc = self._database[id]
        self._database.delete(doc)


class DatabaseService():

    def __init__(self, store):
        self.store = store

    def register(self, document):
        return self.store.create(document)

    def read(self, id):
        return self.store.read(id)

    def update(self, document):
        return self.store.update(document)

    def delete(self, id):
        self.store.delete(id)

    def list(self):
        return self.store.list()
