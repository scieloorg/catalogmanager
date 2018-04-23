# coding = utf-8

import mimetypes


class File:

    def __init__(self, file_name):
        self.name = file_name
        self.content = None
        self.size = None
        self.content_type = None
        if file_name is not None:
            self.content_type = mimetypes.guess_type(file_name)[0]

    def properties(self):
        return {
            'content_size': self.size,
            'content_type': self.content_type,
            'file_name': self.name,
        }
