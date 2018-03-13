# coding = utf-8

import json


class DataStorage:

    def __init__(self):
        pass

    def save(self, record_data):
        content = json.dumps(record_data)
        return 'id'
