import io
import abc

import couchdb


class DocumentNotFound(Exception):
    pass


class BaseDBManager(metaclass=abc.ABCMeta):

    _attachments_properties_key = 'attachments_properties'

    @abc.abstractmethod
    def drop_database(self) -> None:
        return NotImplemented

    @abc.abstractmethod
    def create(self, id, document) -> None:
        return NotImplemented

    @abc.abstractmethod
    def read(self, id) -> dict:
        return NotImplemented

    @abc.abstractmethod
    def update(self, id, document) -> None:
        return NotImplemented

    @abc.abstractmethod
    def delete(self, id) -> None:
        return NotImplemented

    @abc.abstractmethod
    def find(self) -> list:
        return NotImplemented

    @abc.abstractmethod
    def put_attachment(self, id, file_id, content, content_properties) -> None:
        return NotImplemented

    @abc.abstractmethod
    def get_attachment(self, id, file_id) -> io.IOBase:
        return NotImplemented

    @abc.abstractmethod
    def list_attachments(self, id) -> list:
        return NotImplemented

    def add_attachment_properties_to_document_record(self,
                                                     document_id,
                                                     file_id,
                                                     file_properties):
        """
        Acrescenta propriedades (file_properties) do arquivo (file_id)
        ao registro (record)
        Retorna registro (record) atualizado
        """
        _file_properties = {
            k: v
            for k, v in file_properties.items()
            if k not in ['content', 'filename']
        }
        document = self.read(document_id)
        document_record = {
            'document_id': document['document_id'],
            'document_type': document['document_type'],
            'content': document['content'],
            'created_date': document['created_date'],
        }
        properties = document.get(self._attachments_properties_key, {})
        if file_id not in properties.keys():
            properties[file_id] = {}

        properties[file_id].update(
            _file_properties)

        document_record.update(
            {
                self._attachments_properties_key:
                properties
            }
        )
        return document_record

    def get_attachment_properties(self, id, file_id):
        doc = self.read(id)
        return doc.get(self._attachments_properties_key, {}).get(file_id)


class InMemoryDBManager(BaseDBManager):

    def __init__(self, **kwargs):
        self._database_name = kwargs['database_name']
        self._attachments_key = 'attachments'
        self._attachments_properties_key = 'attachments_properties'
        self._database = {}

    @property
    def database(self):
        table = self._database.get(self._database_name)
        if not table:
            self._database[self._database_name] = {}
        return self._database[self._database_name]

    def drop_database(self):
        self._database = {}

    def create(self, id, document):
        self.database.update({id: document})

    def read(self, id):
        doc = self.database.get(id)
        if not doc:
            raise DocumentNotFound
        return doc

    def update(self, id, document):
        _document = self.read(id)
        _document.update(document)
        self.database.update({id: _document})

    def delete(self, id):
        self.read(id)
        del self.database[id]

    def find(self, selector, fields, sort):
        """
        Busca registros de documento por criterios de selecao na base de dados.

        Params:
        selector: criterio para selecionar campo com determinados valores
            Ex.: {'type': 'ART'}
        fields: lista de campos para retornar. Ex.: ['name']
        sort: lista de dict com nome de campo e sua ordenacao.[{'name': 'asc'}]

        Retorno:
        Lista de registros de documento registrados na base de dados
        """
        if len(selector) == 0:
            return [doc for i, doc in self.database.items()]
        results = []
        for id, doc in self.database.items():
            match = True
            for k, v in selector.items():
                if not doc.get(k) == v:
                    match = False
                    break
            if match is True:
                d = {f: doc.get(f) for f in fields}
                d['_id'] = id
                results.append(d)
        return sort_results(results, sort)

    def put_attachment(self, id, file_id, content, content_properties):
        doc = self.read(id)
        if not doc.get(self._attachments_key):
            doc[self._attachments_key] = {}

        if doc[self._attachments_key].get(file_id):
            doc[self._attachments_key][file_id]['revision'] += 1
        else:
            doc[self._attachments_key][file_id] = {}
            doc[self._attachments_key][file_id]['revision'] = 1

        doc[self._attachments_key][file_id]['content'] = content
        doc[self._attachments_key][file_id]['content_type'] = \
            content_properties['content_type']
        doc[self._attachments_key][file_id]['content_size'] = \
            content_properties['content_size']
        self.database.update({id: doc})

    def get_attachment(self, id, file_id):
        doc = self.read(id)
        if (doc.get(self._attachments_key) and
                doc[self._attachments_key].get(file_id)):
            return doc[self._attachments_key][file_id]['content']
        return io.BytesIO()

    def list_attachments(self, id):
        doc = self.read(id)
        return list(doc.get(self._attachments_key, {}).keys())


class CouchDBManager(BaseDBManager):

    def __init__(self, **kwargs):
        self._database_name = kwargs['database_name']
        self._attachments_key = '_attachments'
        self._attachments_properties_key = 'attachments_properties'
        self._database = None
        self._db_server = couchdb.Server(kwargs['database_uri'])
        self._db_server.resource.credentials = (
            kwargs['database_username'],
            kwargs['database_password']
        )

    @property
    def database(self):
        try:
            self._database = self._db_server[self._database_name]
        except couchdb.http.ResourceNotFound:
            self._database = self._db_server.create(self._database_name)
        return self._database

    def drop_database(self):
        if self._database_name:
            try:
                self._db_server.delete(self._database_name)
            except couchdb.http.ResourceNotFound:
                pass

    def create(self, id, document):
        self.database[id] = document

    def read(self, id):
        try:
            doc = dict(self.database[id])
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        return doc

    def update(self, id, document):
        """
        Para atualizar documento no CouchDB, é necessário informar a
        revisão do documento atual. Por isso, é obtido o documento atual
        para que os dados dele sejam atualizados com o registro informado.
        """
        doc = self.read(id)
        doc.update(document)
        self.database[id] = doc

    def delete(self, id):
        doc = self.read(id)
        self.database.delete(doc)

    def find(self, selector, fields, sort):
        """
        Busca registros de documento por criterios de selecao na base de dados.

        Params:
        selector: criterio para selecionar campo com determinados valores
            Ex.: {'type': 'ART'}
        fields: lista de campos para retornar. Ex.: ['name']
        sort: lista de dict com nome de campo e sua ordenacao.[{'name': 'asc'}]

        Retorno:
        Lista de registros de documento registrados na base de dados
        """
        selection_criteria = {
            'selector': selector,
            'fields': fields,
            'sort': sort,
        }
        return [
            dict(document)
            for document in self.database.find(selection_criteria)
        ]

    def put_attachment(self, id, file_id, content, content_properties):
        """
        Para criar anexos no CouchDB, é necessário informar o documento com
        revisão atual. Por isso, é obtido o documento pelo id
        para que os dados dele sejam informados para anexar o arquivo.
        """
        doc = self.read(id)
        self.database.put_attachment(
            doc=doc,
            content=content,
            filename=file_id,
            content_type=content_properties.get('content_type')
        )

    def get_attachment(self, id, file_id):
        doc = self.read(id)
        attachment = self.database.get_attachment(doc, file_id)
        if attachment:
            return attachment.read()
        return io.BytesIO()

    def list_attachments(self, id):
        doc = self.read(id)
        return list(doc.get(self._attachments_key, {}).keys())


def sort_results(results, sort):
    scores = [list() for i in results]
    for _ord in sort:
        field, order = list(_ord.items())[0]

        values = sorted(
            list(
                {doc.get(field) for doc in results}), reverse=(order != 'asc'))
        values = {value: i for i, value in enumerate(values)}
        for i, doc in enumerate(results):
            scores[i].append(values.get(doc.get(field)))
    items = sorted([(tuple(score), i) for i, score in enumerate(scores)])
    r = [results[item[1]] for item in items]
    return r
