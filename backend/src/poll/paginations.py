from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
from collections import OrderedDict


class SurveyPassingPagination(LimitOffsetPagination):
    max_limit = 10000
    default_limit = 30

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('survey_Passing', data)
        ]))


class PollPagination(LimitOffsetPagination):
    max_limit = 100
    default_limit = 30

    def get_offset(self, request):
        w_offset = super().get_offset(request)
        offset = (w_offset - 1) * self.limit
        if offset < 0:
            return 0
        return offset

    def get_next_link(self):
        if self.offset + self.limit >= self.count:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + 2
        return replace_query_param(url, self.offset_query_param, offset)

    def get_previous_link(self):
        if self.offset <= 0:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        if self.offset - self.limit <= 0:
            return replace_query_param(url, self.offset_query_param, 1)

        offset = self.offset
        return replace_query_param(url, self.offset_query_param, offset)

    def get_paginated_response(self, data):
        pages = self.count / self.limit
        pages = round(pages + 0.5)

        return Response(OrderedDict([
            ('count', pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('result', data)
        ]))
