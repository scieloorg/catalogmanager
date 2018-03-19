import abc
from enum import Enum
from uuid import uuid4


class DocumentRecord(metaclass=abc.ABCMeta):

    class DocumentType(Enum):
        ARTICLE = 'ART'
        ASSET = 'ASS'
        ISSUE = 'ISS'
        JOURNAL = 'JOR'

    def __init__(self, content):
        self.content = content
        self._document_type = None
        self._created_date = None

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
        document = None
        if document_record['document_type'] == self.DocumentType.ARTICLE.value:
            document = ArticleRecord(
                self.content,
                document_record['document_id']
            )
            document.created_date = document_record['created_date']
        return document


class ArticleRecord(DocumentRecord):

    def __init__(self, content, document_id=uuid4().hex):
        super().__init__(content)
        self.document_type = self.DocumentType.ARTICLE
        self._document_id = document_id

    @property
    def document_id(self):
        return self._document_id

    def input(self):
        return {
            'document_id': self.document_id,
            'document_type': self.document_type.value,
            'content': self.content,
            'created_date': self.created_date,
        }
