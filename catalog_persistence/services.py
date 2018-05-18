from datetime import datetime
from enum import Enum
from uuid import uuid4


class ChangeType(Enum):
    CREATE = 'C'
    UPDATE = 'U'
    DELETE = 'D'


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

    def register_change(self,
                        document_record,
                        change_type,
                        attachment_id=None):
        change_record = {
            'change_id': uuid4().hex,
            'document_id': document_record['document_id'],
            'document_type': document_record['document_type'],
            'type': change_type.value,
            'created_date': str(datetime.utcnow().timestamp()),
            'seqnum': self.seqnum_generator.new(),
        }
        if attachment_id:
            change_record.update({'attachment_id': attachment_id})
        self.changes_db_manager.create(
            change_record['change_id'],
            change_record
        )
        return change_record['change_id']


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
            'created_date': document['created_date']
        }
        if document.get('updated_date'):
            document_record['updated_date'] = document['updated_date']
        attachments = self.db_manager.list_attachments(document_id)
        if attachments:
            document_record['attachments'] = \
                self.db_manager.list_attachments(document_id)
        return document_record

    def update(self, document_id, document_record):
        """
        Atualiza o registro de um documento e a mudança na base de dados.

        Params:
        document_id: ID do documento a ser atualizado
        document_record: registro de documento a ser atualizado

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
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

        Erro:
        DocumentNotFound: documento não encontrado na base de dados.
        """
        self.db_manager.delete(document_id)
        self.changes_service.register_change(
            document_record, ChangeType.DELETE)

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
        document_record = self.db_manager. \
            add_attachment_properties_to_document_record(
                document_id,
                file_id,
                file_properties
            )
        self.update(document_id, document_record)

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
