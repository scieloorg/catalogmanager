
from cornice.resource import resource
from pyramid.response import Response

import catalogmanager


@resource(collection_path='/changes', path='/changes/{id}', renderer='json')
class ChangeAPI:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    def collection_get(self):
        limit = 0
        if self.request.GET.get('limit'):
            limit = int(self.request.GET['limit'])
        changes = catalogmanager.list_changes(
            last_sequence=self.request.GET.get('since', ''),
            limit=limit,
            **self.request.db_settings
        )
        return Response(json=changes)
