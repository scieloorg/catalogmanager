# coding = utf-8


class ArticleStorage:

    def __init__(self, datastorage):
        self.datastorage = datastorage

    def register(self, record_id, record_data):
        self.datastorage.register(record_data)
        self.datastorage.register_changes('article', record_id)
        return self.location(record_id)

    def location(self, id):
        return '{}/assets/{}'.format(
            self.datastorage.location(), id)


class AssetStorage:

    def __init__(self, datastorage):
        self.datastorage = datastorage

    def register(self, record_id, record_data):
        self.datastorage.register(record_data)
        self.datastorage.register_changes('asset', record_id)
        return self.location(record_id)

    def location(self, id):
        return '{}/articles/{}'.format(
            self.datastorage.location(), id)
