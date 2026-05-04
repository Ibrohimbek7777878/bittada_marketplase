"""Pagination defaults — predictable shape on every list endpoint."""
from __future__ import annotations

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):  # type: ignore[no-untyped-def]
        return Response({
            "count": self.page.paginator.count,
            "page": self.page.number,
            "pages": self.page.paginator.num_pages,
            "page_size": self.get_page_size(self.request),
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })
