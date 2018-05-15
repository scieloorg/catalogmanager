
from cornice.resource import resource, view
from pyramid.response import Response

import catalogmanager


@resource(collection_path='/changes', path='/changes/{id}', renderer='json')
class ChangeAPI:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    @view(content_type='multipart/form-data')
    def collection_post(self):
        limit = 0
        if self.request.POST.get('limit'):
            limit = int(self.request.POST['limit'])
        changes = catalogmanager.list_changes(
            last_sequence=self.request.POST.get('last_sequence'),
            limit=limit,
            **self.request.db_settings
        )
        return Response(json=changes)
