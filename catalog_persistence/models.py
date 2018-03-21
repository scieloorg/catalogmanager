from enum import Enum
from uuid import uuid4


class DocumentType(Enum):
    ARTICLE = 'ART'
    ASSET = 'ASS'
    ISSUE = 'ISS'
    JOURNAL = 'JOR'


class ArticleRecord:

    def __init__(self, content=None, document_id=uuid4().hex):
        self.document_id = document_id
        self.document_type = DocumentType.ARTICLE
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
        self.document_type = DocumentType.ARTICLE
        self.created_date = document.get('created_date')
        return self
