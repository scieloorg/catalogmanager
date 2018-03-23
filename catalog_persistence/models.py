from enum import Enum


class RecordType(Enum):
    DOCUMENT = 'DOC'
    ARTICLE = 'ART'
    ASSET = 'AST'
    ISSUE = 'ISS'
    JOURNAL = 'JOR'


def get_record(document_id,
               document_type=RecordType.DOCUMENT,
               content='',
               created_date=None,
               updated_date=None):
        record = {
            'document_id': document_id,
            'document_type': document_type.value,
            'content': content
        }
        if created_date:
            record.update({'created_date': str(created_date.timestamp())})
        if updated_date:
            record.update({'updated_date': str(updated_date.timestamp())})
        return record
