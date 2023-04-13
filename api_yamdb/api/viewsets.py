from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class CreateListDelVS(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'slug'

    def create(self, request, *args, **kwargs):
        """
        Shows a paginated list of all objects upon creation
        instead of default detail view
        """
        super().create(request, *args, **kwargs)
        paginated_response = self.list(request, *args, **kwargs)
        return Response(
            paginated_response.data,
            status=status.HTTP_201_CREATED
        )
