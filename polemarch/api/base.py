from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route


class GenericViewSet(viewsets.GenericViewSet):
    serializer_class_one = None
    model = None

    def get_serializer_class(self):
        if self.kwargs.get("pk", False) or self.action == "create":
            if self.serializer_class_one is not None:
                return self.serializer_class_one
        return super(GenericViewSet, self).get_serializer_class()

    def _get_extra_queryset(self):
        aval_projs = self.request.user.related_objects.values_list('projects',
                                                                   flat=True)
        return self.queryset.filter(
            Q(related_objects__user=self.request.user) |
            Q(related_objects__projects__in=aval_projs)
        ).distinct()

    def get_queryset(self):
        if self.queryset is None:
            assert self.model is not None, (
                "'%s' should either include a `queryset` or `model` attribute,"
                " or override the `get_queryset()` method."
                % self.__class__.__name__
            )
            self.queryset = self.model.objects.all()
        if not self.request.user.is_staff and self.queryset.model != User:
            self.queryset = self._get_extra_queryset()
        return super(GenericViewSet, self).get_queryset()

    def get_paginated_route_response(self, queryset, serializer_class=None):
        if serializer_class is None:
            serializer_class = self.get_serializer_class()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=["post", "put", "delete", "get"])
    def permissions(self, request, pk=None):
        # pylint: disable=unused-argument
        serializer = self.get_serializer(self.get_object())
        return serializer.permissions(request)

    @list_route(methods=["post"])
    def filter(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(**request.data.get("filter", {}))
        queryset = queryset.exclude(**request.data.get("exclude", {}))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReadOnlyModelViewSet(GenericViewSet,
                           viewsets.ReadOnlyModelViewSet):
    pass


class HistoryModelViewSet(GenericViewSet,
                          viewsets.ReadOnlyModelViewSet,
                          viewsets.mixins.DestroyModelMixin):
    pass


class ModelViewSetSet(GenericViewSet, viewsets.ModelViewSet):
    pass
