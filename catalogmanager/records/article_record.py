# coding=utf-8

from catalog_persistence import models
from ..models import article_model


class AssetRecord(models.DocumentRecord):

    def __init__(self, document, document_id=uuid4().hex):
        document['document_type'] = self.DocumentType.ASSET
        super().__init__(document, document_id)
        self.document_type = self.DocumentType.ASSET


class ArticleRecord(DocumentRecord):

    def __init__(self, document, document_id=uuid4().hex):
        document['document_type'] = self.DocumentType.ARTICLE
        super().__init__(document, document_id)
        self.document_type = self.DocumentType.ARTICLE
