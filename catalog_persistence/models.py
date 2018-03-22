from enum import Enum
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

    def serialize(self):
        return {
            'document_id': self.document_id,
            'document_type': self.document_type.value,
            'content': self.content
        }

    def deserialize(self, document):
        self.content = document.get('content')
        self.document_id = document.get('document_id')
        self.document_type = RecordType(
            document.get('document_type', RecordType.DOCUMENT)
        )
        self.created_date = document.get('created_date')
        return self
