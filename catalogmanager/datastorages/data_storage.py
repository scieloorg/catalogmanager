# coding = utf-8

import json


class DataStorage:

    def __init__(self):
        pass

    def register(self, record_data):
        content = json.dumps(record_data)
        return record_data.get('id')

    def location(self):
        return '{}'.format('APP_URI')

    def register_changes(self, element_type, element_id):
        pass
