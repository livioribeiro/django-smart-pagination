from django.core.paginator import Page
from django import template
from django.template import TemplateSyntaxError

from .. import pagination, error_messages as errors

register = template.Library()


@register.tag
def paginate(parser, token):
    contents = token.split_contents()

    if len(contents) == 1:
        raise TemplateSyntaxError(errors.MISSING_FIRST_ARG)
    elif len(contents) == 2:
        raise TemplateSyntaxError(errors.MISSING_SECOND_ARG)
    elif len(contents) == 3:
        tag_name, page_obj, num_links = contents
        page_kwarg = None
    elif len(contents) == 4:
        tag_name, page_obj, num_links, page_kwarg = contents
    else:
        raise TemplateSyntaxError(errors.WRONG_ARGS.format(contents[0]))

    nodelist = parser.parse(('endpaginate',))
    parser.delete_first_token()

    return PaginationNode(nodelist, page_obj, num_links, page_kwarg)


class PaginationNode(template.Node):
    def __init__(self, nodelist, page_obj, num_links, page_kwarg):
        self.nodelist = nodelist
        self.page_obj = page_obj
        self.num_links = num_links
        self.page_kwarg = page_kwarg.strip('"\'') if page_kwarg is not None else None

    def render(self, context):
        request = context.get('request', None)

        page_obj = template.Variable(self.page_obj).resolve(context)

        if not isinstance(page_obj, Page):
            raise template.TemplateSyntaxError(errors.WRONG_FIRST_ARG)

        try:
            num_links = int(self.num_links)
        except ValueError:
            if self.num_links.startswith("'") or self.num_links.startswith('"'):
                raise template.TemplateSyntaxError(errors.WRONG_SECOND_ARG)

            num_links = template.Variable(self.num_links).resolve(context)

            if not isinstance(num_links, int):
                raise template.TemplateSyntaxError(errors.WRONG_SECOND_ARG)

        query = pagination.process_querystring(request, self.page_kwarg) if request else None

        paginator = pagination.make_paginator(page_obj, num_links)

        if query:
            paginator.query = query

        context.update({'paging': paginator})

        return self.nodelist.render(context)