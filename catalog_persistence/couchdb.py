#!/usr/bin/python
from datetime import datetime

import couchdb


class CouchDBManager:

    def __init__(self, settings):
        self._db_server = couchdb.Server(settings['couchdb.uri'])
        self._db_name = settings['couchdb.db_name']
        self._db_server.resource.credentials = (
            settings['couchdb.username'],
            settings['couchdb.password']
        )
        try:
            self._database = self._db_server[self._db_name]
        except couchdb.http.ResourceNotFound:
            self._database = self._db_server.create(self._db_name)

    def drop_database(self):
        self._db_server.delete(self._db_name)

    def create(self, document):
        doc = {}
        for key, value in document.items():
            if type(value) == str:
                doc.update({key: value})
            elif type(value) == datetime:
                doc.update({key: str(value.timestamp())})

        id, rev = self._database.save(doc)
        return self._database[id]

    def get_by_id(self, id):
        return self._database[id]
