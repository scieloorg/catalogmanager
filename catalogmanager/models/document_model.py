# coding = utf-8


class DocumentType(Enum):
    ARTICLE = 'ART'
    ASSET = 'ASS'
    ISSUE = 'ISS'
    JOURNAL = 'JOR'


class Document:

    def __init__(self):
        pass

    def serialize(self):
        record = {}
        record['content'] = self.get_content()

        return record
