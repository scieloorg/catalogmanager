from enum import Enum
from datetime import datetime
from uuid import uuid4


class RecordType(Enum):
    DOCUMENT = 'DOC'
    ARTICLE = 'ART'
    ASSET = 'ASS'
    ISSUE = 'ISS'
    JOURNAL = 'JOR'


class Record:

    def __init__(self, content=None, document_id=uuid4().hex,
                 document_type=RecordType.DOCUMENT):
        self.document_id = document_id
        self.document_type = document_type
        self.content = content
        self.created_date = None
        self.updated_date = None

    def serialize(self):
        record = {
            'document_id': self.document_id,
            'document_type': self.document_type.value,
            'content': self.content
        }
        if self.created_date:
            record.update({'created_date': str(self.created_date.timestamp())})
        if self.updated_date:
            record.update({'updated_date': str(self.updated_date.timestamp())})
        return record

    def deserialize(self, document):
        self.content = document.get('content')
        self.document_id = document.get('document_id')
        self.document_type = RecordType(
            document.get('document_type', RecordType.DOCUMENT)
        )
        if document.get('created_date'):
            self.created_date = (
                datetime.fromtimestamp(float(document['created_date']))
            )
        if document.get('updated_date'):
            self.updated_date = (
                datetime.fromtimestamp(float(document['updated_date']))
            )
        return self
