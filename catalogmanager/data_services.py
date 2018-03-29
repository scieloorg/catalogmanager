# coding = utf-8


class DataServices:

    def __init__(self, name):
        self.name = name

    def location(self, record_id):
        return '/{}/{}'.format(self.name, record_id)

    def get_article_id(self, article_url):
        _, _, record_id = article_url.split('/')
        return record_id
