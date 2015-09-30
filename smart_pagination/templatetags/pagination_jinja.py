from django.core.paginator import Page
from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError, TemplateError

from .. import pagination, error_messages as errors


class PaginationExtension(Extension):
    tags = {'paginate'}

    def parse(self, parser):
        self.lineno = next(parser.stream).lineno

        request = nodes.Name('request', 'load')
        try:
            page_obj = parser.parse_expression()
        except TemplateSyntaxError:
            raise TemplateSyntaxError(errors.MISSING_FIRST_ARG, self.lineno)

        args = [request, page_obj]

        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            raise TemplateSyntaxError(errors.MISSING_SECOND_ARG, self.lineno)

        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())

        call_node = self.call_method('_make_paginator', args)
        body = parser.parse_statements(['name:endpaginate'], drop_needle=True)
        body.insert(0, nodes.Assign(nodes.Name('paging', 'store'), call_node))
        return body

    def _make_paginator(self, request, page_obj, num_links, page_kwarg=None):
        if not isinstance(page_obj, Page):
            raise TemplateSyntaxError(errors.WRONG_FIRST_ARG, self.lineno)

        if not isinstance(num_links, int):
            raise TemplateSyntaxError(errors.WRONG_SECOND_ARG, self.lineno)

        paginator = pagination.make_paginator(page_obj, num_links)
        query = pagination.process_querystring(request, page_kwarg) if request else None

        if query:
            paginator.query = query

        return paginator
