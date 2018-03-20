import abc
from enum import Enum
from uuid import uuid4


class DocumentRecord(metaclass=abc.ABCMeta):

    class DocumentType(Enum):
        ARTICLE = 'ART'
        ASSET = 'ASS'
        ISSUE = 'ISS'
        JOURNAL = 'JOR'

    def __init__(self, document, document_id):
        self.content = document.get('content')
        self._document_id = document_id
        self._document_type = (
            self.DocumentType(document['document_type'])
            if document.get('document_type') else None
        )
        self._created_date = document.get('created_date')

    @property
    def document_id(self):
        return self._document_id

    @property
    def document_type(self):
        return self._document_type

    @document_type.setter
    def document_type(self, document_type):
        self._document_type = document_type

    @property
    def created_date(self):
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        self._created_date = created_date

    def output(self):
        return self


class ArticleRecord(DocumentRecord):

    def __init__(self, document, document_id=uuid4().hex):
        document['document_type'] = self.DocumentType.ARTICLE
        super().__init__(document, document_id)

    def input(self):
        return {
            'document_id': self.document_id,
            'document_type': self.document_type.value,
            'content': self.content,
            'created_date': self.created_date,
        }
