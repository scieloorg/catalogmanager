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
        self.content = document['content']
        self._document_id = document_id
        self._document_type = None
        self._created_date = None

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

    def output(self, document_record):
        self.document_type = self.DocumentType(
            document_record['document_type']
        )
        self.created_date = document_record['created_date']
        return self


class ArticleRecord(DocumentRecord):

    def __init__(self, document, document_id=uuid4().hex):
        super().__init__(document, document_id)
        self.document_type = self.DocumentType.ARTICLE

    def input(self):
        return {
            'document_id': self.document_id,
            'document_type': self.document_type.value,
            'content': self.content,
            'created_date': self.created_date,
        }
