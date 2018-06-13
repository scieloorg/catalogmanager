import io
import abc
import operator
from enum import Enum
from itertools import islice

import couchdb


class UpdateFailure(Exception):

    def __init__(self, message):
        self.message = message


class DocumentNotFound(Exception):
    pass


class DBFailed(Exception):
    pass


class QueryOperator(Enum):
    GREATER_THAN = 'gt'
    GREATER_THAN_EQUAL = 'ge'
    LESS_THAN = 'lt'
    LESS_THAN_EQUAL = 'le'
    NOT_EQUAL = 'ne'


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
    def find(self, filter, fields, sort, limit=0) -> list:
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
                                                     document_record,
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
        properties = document_record.get(self._attachments_properties_key, {})
        properties[file_id] = _file_properties

        document_record.update(
            {
                self._attachments_properties_key:
                properties
            }
        )

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
        document['revision'] = 1
        document['_rev'] = 1
        self.database.update({id: document})

    def read(self, id):
        doc = self.database.get(id)
        if not doc:
            raise DocumentNotFound
        doc['document_rev'] = doc['revision']
        doc['_rev'] = doc['_rev']

        return doc

    def update(self, id, document):
        _document = self.read(id)
        if _document.get('revision') != document.get('document_rev'):
            raise UpdateFailure(
                'You are trying to update a record which data is out of date')
        _document.update(document)
        _document['revision'] += 1
        self.database.update({id: _document})

    def new_update(self, id, document):
        _document = self.read(id)
        if _document.get('_rev') != document.get('_rev'):
            raise UpdateFailure(
                'UpdateFailure')
        _document.update(document)
        _document['_rev'] += 1
        self.database.update({id: _document})

    def delete(self, id):
        self.read(id)
        del self.database[id]

    def find(self, filter, fields, sort, limit=0):
        """
        Busca registros de documento por criterios de selecao na base de dados.

        Params:
        filter: criterio para selecionar campo com determinados valores ou
            vazio para todos
            Ex.: {'type': 'ART', 'id': [(QueryOperator.EQUAL, 1000)]}
        fields: lista de campos para retornar ou vazio para todos.
            Ex.: ['name']
        sort: lista de dict com nome de campo e sua ordenacao.
            Ex.: [{'name': 'asc'}]
        limit: (Opcional) Número máximo de registros a retornar.

        Retorno:
        Lista de registros de documento registrados na base de dados
        """
        def match_doc(doc, filter):
            """
            Verifica se doc atende os critérios de seleção de filter.

            :param doc: registro de documento da base de dados.
            :type doc: dict.
            :param filter: chaves/campos para aplicação do filtro com valor que
                corresponde ao filtro a ser verificado no doc. Esse filtro pode
                ser do tipo str ou list, onde o list contém uma tupla com
                operação do filtro e valor do filtro a ser aplicado.
                Ex.: {'type': 'ART', 'id': [(QueryOperator.EQUAL, 1000)]}
            :type filter: dict.

            :returns: True se documento atende a todos os critérios do filtro.
                Caso contrário, False.
            :rtype: bool.
            """
            result = []
            for field_name, field_filter in filter.items():
                if isinstance(filter, dict):
                    filter_result = [
                        getattr(operator, field_operator.value)(
                            doc.get(field_name),
                            filter_value if filter_value else ''
                        )
                        for field_operator, filter_value in field_filter
                    ]
                    result.extend(filter_result)
                else:
                    result.append(doc.get(field_name) == field_filter)

            return all(result)

        if len(filter) == 0:
            results = list(
                islice(self.database.values(),
                       limit if limit else None)
            )
        else:
            results = []
            for doc in self.database.values():
                if match_doc(doc, filter):
                    if fields:
                        d = {f: doc.get(f) for f in fields}
                        results.append(d)
                    else:
                        results.append(doc)
                    if limit and len(results) >= limit:
                        break
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
            doc['document_rev'] = doc['_rev']
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        return doc

    def new_update(self, id, document):
        """
        Para atualizar documento no CouchDB, é necessário informar a
        revisão do documento atual. Por isso, é obtido o documento atual
        para que os dados dele sejam atualizados com o registro informado.
        """
        try:
            self.database[id] = document
        except couchdb.http.ResourceNotFound:
            raise DocumentNotFound
        except:
            raise UpdateFailure('UpdateFailure')

    def update(self, id, document):
        """
        Para atualizar documento no CouchDB, é necessário informar a
        revisão do documento atual. Por isso, é obtido o documento atual
        para que os dados dele sejam atualizados com o registro informado.
        """
        doc = self.read(id)
        if doc.get('_rev') != document.get('document_rev'):
            raise UpdateFailure(
                'You are trying to update a record which data is out of date')

        doc.update(document)
        self.database[id] = doc

    def delete(self, id):
        doc = self.read(id)
        self.database.delete(doc)

    def find(self, filter, fields, sort, limit=0):
        """
        Busca registros de documento por criterios de selecao na base de dados.
        # XXX: A biblioteca couchdb-python permite somente um critério de sele-
        ção para cada campo de filter, o que não possibilita a criação de fil-
        tro para selecionar campo com valor entre dois valores, por exemplo.

        Params:
        filter: criterio para selecionar campo com determinados valores ou
            vazio para todos
            Ex.: {'type': 'ART', 'id': [(QueryOperator.EQUAL, 1000)]}
        fields: lista de campos para retornar ou vazio para todos.
            Ex.: ['name']
        sort: lista de dict com nome de campo e sua ordenacao.
            Ex.: [{'name': 'asc'}]
        limit: (Opcional) Número máximo de registros da lista.

        Retorno:
        Lista de registros de documento registrados na base de dados
        """
        def create_selector(filter, sort):
            if not filter and sort:
                filter = {
                    sorter_name: {
                        '$' + QueryOperator.GREATER_THAN.value: None
                    }
                    for sorter in sort
                    for sorter_name, __ in sorter.items()
                }
            else:
                for field_name, field_filter in filter.items():
                    if isinstance(field_filter, list):
                        filter[field_name] = {
                            '$' + field_criteria[0].value: field_criteria[1]
                            for field_criteria in field_filter
                        }
            return filter

        def check_sort_index(sort):
            indexes = self.database.index()
            found_index = [
                index['def']['fields']
                for index in iter(indexes)
                if index['def']['fields'] == sort
            ]
            if not found_index:
                index_key = '_'.join(
                    [
                        sorter_key
                        for sorter in sort
                        for sorter_key in sorter.keys()
                    ]
                )
                indexes[index_key, index_key] = sort

        selector = create_selector(filter, sort)
        if sort and sort[0]:
            check_sort_index(sort)
        selection_criteria = {
            'selector': selector,
            'fields': fields,
            'sort': sort,
        }
        if limit > 0:
            selection_criteria.update({'limit': limit})

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
