
class ChangeServices:

    def __init__(self, database_service):
        self.database_service = database_service

    def history(self, begin_date=None, end_date=None):
