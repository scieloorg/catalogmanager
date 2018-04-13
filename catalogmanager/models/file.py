# coding = utf-8

import os
import mimetypes


class File:

    def __init__(self, file_fullpath):
        self.file_fullpath = file_fullpath
        self.name = None
        self.path = None
        self.size = None
        self.content_type = None
        self.content = None
        if file_fullpath is not None and os.path.isfile(file_fullpath):
            self.name = os.path.basename(file_fullpath)
            self.path = os.path.dirname(file_fullpath)
            self.content_type = mimetypes.guess_type(file_fullpath)[0]
