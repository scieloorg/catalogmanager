# coding = utf-8


class DataServices:

    def __init__(self, name):
        self.name = name

    def location(self, record_id):
        return '/{}/{}'.format(self.name, record_id)
