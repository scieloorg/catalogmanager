# coding = utf-8

import mimetypes


class File:

    def __init__(self, file_fullpath):
        self.file_fullpath = file_fullpath
        self.name = None
        self.path = None
        self.size = None
        self.content_type = None
        self.content = None
        if file_fullpath is not None:
            self.name = file_fullpath
            self.content_type = mimetypes.guess_type(file_fullpath)[0]

    def properties(self):
        return {
            'content_size': self.size,
            'content_type': self.content_type,
            'file_fullpath': self.file_fullpath,
            'file_name': self.name,
            'file_path': self.path,
        }
