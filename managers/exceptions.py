# coding=utf-8


class ManagerFileError(Exception):

    def __init__(self, message):
        self.message = message
