# coding = utf-8

from catalog_persistence.databases import (
    DatabaseService,
)


class DataServices:

    def __init__(self, db_manager, changes_db_manager):
        self.db_service = DatabaseService(
                db_manager,
                changes_db_manager
            )
        self.name = self.db_service.db_manager.database_name

    def register(self, record_id, record_data):
        return self.db_service.register(record_id, record_data)

    def location(self, record_id):
        return '/{}/{}'.format(self.name, record_id)
