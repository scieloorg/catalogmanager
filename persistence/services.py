from datetime import datetime
from enum import Enum

from prometheus_client import Summary

from .databases import QueryOperator, UpdateFailure


REQUEST_TIME_CHANGES_UPD = Summary(
    'changes_service_upd_request_processing_seconds',
    'Time spent processing changes service upd ')
REQUEST_TIME_CHANGES_LIST = Summary(
    'changes_service_list_request_processing_seconds',
    'Time spent processing changes service list ')
REQUEST_TIME_DOC_UPD = Summary(
    'db_service_doc_upd_request_processing_seconds',
    'Time spent processing db_service doc upd')
REQUEST_TIME_DOC_READ = Summary(
    'db_service_doc_read_request_processing_seconds',
    'Time spent processing db_service doc read')
REQUEST_TIME_DOC_FIND = Summary(
    'db_service_doc_FIND_request_processing_seconds',
    'Time spent processing db_service doc find')
REQUEST_TIME_ATT_READ = Summary(
    'db_service_att_read_request_processing_seconds',
    'Time spent processing db_service att read')
REQUEST_TIME_ATT_UPD = Summary(
    'db_service_att_upd_request_processing_seconds',
    'Time spent processing db_service att upd ')


class ChangeType(Enum):
    CREATE = 'C'
    UPDATE = 'U'
    DELETE = 'D'


class SortOrder(Enum):
    ASC = 'asc'
    DESC = 'desc'


class ChangesService:
    """
    Changes Service é responsável por persistir registros de mudanças(dicts)
    em um DBManager e de mudanças relacionadas a eles em outro DBManager, ambos
    informados na instanciação desta classe.

    changes_db_manager:
        Instância do DBManager para persistir registro de mudanças
    seqnum_generator:
        Instância do DBManager para persistir número sequencial
    """

    def __init__(self, changes_db_manager, seqnum_generator):
        self.changes_db_manager = changes_db_manager
        self.seqnum_generator = seqnum_generator

    @REQUEST_TIME_CHANGES_UPD.time()
    def register_change(self,
                        document_record,
                        change_type,
                        attachment_id=None):
        sequencial = self.seqnum_generator.new()
        change_record = {
            'change_id': sequencial,
            'document_id': document_record['document_id'],
            'document_type': document_record['document_type'],
            'type': change_type.value,
            'created_date': str(datetime.utcnow().timestamp()),
            'record_id': str(sequencial),
        }
        if attachment_id:
            change_record.update({'attachment_id': attachment_id})
        self.changes_db_manager.create(
            change_record['record_id'],
            change_record
        )
        return change_record['record_id']


class DatabaseService:
    """
    Database Service é responsável por persistir registros de documentos(dicts)
    em um DBManager e de mudanças relacionadas a eles em outro DBManager, ambos
    informados na instanciação desta classe.

    db_manager:
        Instância do DBManager para persistir registro de documentos
    changes_services:
        Instância do ChangesService para gerir registros de mudanças
    """

    def __init__(self, db_manager, changes_service):
        self.db_manager = db_manager
        self.changes_service = changes_service

    @REQUEST_TIME_DOC_UPD.time()
    def register(self, document_id, document_record):
        """
        Persiste registro de um documento e a mudança na base de dados.

        Params:
        document_id: ID do documento
        document_record: registro do documento
        """
        document_record.update({
            'created_date': str(datetime.utcnow().timestamp())
        })
        self.db_manager.create(document_id, document_record)
        self.changes_service.register_change(
            document_record, ChangeType.CREATE)

    @REQUEST_TIME_DOC_READ.time()
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
        document = self.db_manager.read(document_id)
        document_record = {
            'document_id': document['document_id'],
            'document_type': document['document_type'],
            'content': document['content'],
            'created_date': document['created_date'],
            'document_rev': document['document_rev'],
        }
        for optional in ['updated_date', 'deleted_date']:
            if optional in document.keys():
                document_record[optional] = document[optional]
        attachments = self.db_manager.list_attachments(document_id)
        if attachments:
            document_record['attachments'] = \
                self.db_manager.list_attachments(document_id)
        return document_record

    @REQUEST_TIME_DOC_UPD.time()
    def update(self, document_id, document_record):
        """
        Atualiza o registro de um documento e a mudança na base de dados.

        Params:
        document_id: ID do documento a ser atualizado
        document_record: registro de documento a ser atualizado

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
        UpdateFailure: dados do document_record estão desatualizados.
        """
        document_record.update({
            'updated_date': str(datetime.utcnow().timestamp())
        })
        self.db_manager.update(document_id, document_record)
        self.changes_service.register_change(
            document_record, ChangeType.UPDATE)

    def delete(self, document_id, document_record):
        """
        Remove registro de um documento e a mudança na base de dados.

        Params:
        document_id: ID do documento a ser deletado
        document_record: registro de documento a ser deletado

        Erros:
        DocumentNotFound: documento não encontrado na base de dados.
        UpdateFailure: documento não apagado da base de dados.
        """
        document_record.update({
            'deleted_date': str(datetime.utcnow().timestamp()),
        })
        try:
            self.db_manager.update(document_id, document_record)
            self.changes_service.register_change(
                document_record, ChangeType.DELETE)
        except UpdateFailure:
            raise UpdateFailure(
                'Document {} not allowed to delete'.format(document_id))

    @REQUEST_TIME_DOC_FIND.time()
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
        return self.db_manager.find(selector, fields, sort)

    @REQUEST_TIME_ATT_UPD.time()
    def put_attachment(self, document_id, file_id, content, file_properties):
        """
        Anexa arquivo no registro de um documento pelo ID do documento e
        registra mudança na base de dados.

        Params:
        document_id: ID do documento ao qual deve ser anexado o arquivo
        file_id: identificação do arquivo a ser anexado
        content: conteúdo do arquivo a ser anexado
        file_properties: propriedades do arquivo (MIME type, tamanho etc.)

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
        """
        self.db_manager.put_attachment(document_id,
                                       file_id,
                                       content,
                                       file_properties)
        document_record = self.db_manager.read(document_id)
        self.db_manager. \
            add_attachment_properties_to_document_record(
                document_record,
                file_id,
                file_properties
            )
        self.update(document_id, document_record)

    @REQUEST_TIME_ATT_READ.time()
    def get_attachment(self, document_id, file_id):
        """
        Recupera arquivo anexos ao registro de um documento pelo ID do
        documento e ID do anexo.
        Params:
        document_id: ID do documento ao qual o arquivo está anexado
        file_id: identificação do arquivo anexado a ser recuperado

        Retorno:
        Arquivo anexo

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
        """
        return self.db_manager.get_attachment(document_id, file_id)

    def get_attachment_properties(self, document_id, file_id):
        """
        Recupera arquivo anexos ao registro de um documento pelo ID do
        documento e ID do anexo.
        Params:
        document_id: ID do documento ao qual o arquivo está anexado
        file_id: identificação do arquivo anexado a ser recuperado

        Retorno:
        Arquivo anexo

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
        """
        return self.db_manager.get_attachment_properties(document_id, file_id)

    @REQUEST_TIME_CHANGES_LIST.time()
    def list_changes(self, last_sequence, limit):
        """
        Busca registros de mudança a partir do sequencial informado e retorna
        a lista com, no máximo, o limite informado.

        Params:
        :param last_sequence: sequencial de mudança, que deve ser a referência
            para a busca dos sequenciais a serem listados.
        :param limit: limite máximo de registros de mudança que devem ser
            listados.

        Retorno:
        Lista de registros de mudança
        """
        def convert_change_type(change):
            change.update({'type': ChangeType(change['type']).name})
            return change

        fields = [
            'change_id',
            'document_id',
            'document_type',
            'type',
            'created_date'
        ]
        filter = {
            'change_id': [
                (QueryOperator.GREATER_THAN,
                 last_sequence if last_sequence else None)
            ]
        }
        sort = [{'change_id': SortOrder.ASC.value}]
        changes = self.changes_service.changes_db_manager.find(
                                               fields=fields,
                                               limit=limit,
                                               filter=filter,
                                               sort=sort)
        return [
            convert_change_type(change)
            for change in changes
        ]
