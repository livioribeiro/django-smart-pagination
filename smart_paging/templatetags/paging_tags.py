import math
from django import template

register = template.Library()


class Page:
    def __init__(self, current_number, page_number):
        self.is_current = current_number == page_number
        self.number = page_number


class Paginator:
    def __init__(self, first_page, prev_page, page_range, next_page, last_page, current_page):
        pages = list()
        for page_number in page_range:
            pages.append(Page(current_page, page_number))

        self.first = first_page
        self.prev = prev_page
        self.pages = pages
        self.next = next_page
        self.last = last_page


def make_paginator(page_obj, num_links) -> Paginator:
    number = page_obj.number
    page_count = len(page_obj.paginator.page_range)

    prev_page = page_obj.previous_page_number() if page_obj.has_previous() else None
    next_page = page_obj.next_page_number() if page_obj.has_next() else None

    middle_point = math.ceil(num_links / 2)
    first_page = page_obj.paginator.page_range[0] if page_count > num_links and number > middle_point else None

    last_page = page_obj.paginator.page_range[-1]

    if num_links % 2 == 1:
        not_last_section = number <= (last_page - middle_point)
    else:
        not_last_section = number < (last_page - middle_point)

    last_page = last_page if page_count > num_links and not_last_section else None

    if first_page is None:
        page_range = page_obj.paginator.page_range[:num_links]
    elif last_page is None:
        page_range = page_obj.paginator.page_range[-num_links:]
    else:
        start = number - (middle_point - 1) - 1  # zero indexed
        end = number + middle_point - 1  # zero indexed

        # fix for even number of links
        if num_links % 2 == 0:
            end += 1

        page_range = page_obj.paginator.page_range[start:end]

    return Paginator(first_page, prev_page, page_range, next_page, last_page, number)


@register.tag
def paging(parser, token):
    contents = token.split_contents()
    try:
        if len(contents) == 3:
            tag_name, page_obj, num_links = contents
            page_kwarg = 'page'
        elif len(contents) == 4:
            tag_name, page_obj, num_links, page_kwarg = contents
        else:
            raise template.TemplateSyntaxError()
    except template.TemplateSyntaxError:
        raise template.TemplateSyntaxError(
            '"{}" requires a "Page" object,'
            ' the number of links to show'
            ' and, optionally, the "page_kwarg" value'.format(token.contents.split()[0])
        )

    num_links = int(num_links)

    nodelist = parser.parse(('endpager',))
    parser.delete_first_token()

    return PaginationNode(nodelist, page_obj, num_links, page_kwarg)


class PaginationNode(template.Node):
    def __init__(self, nodelist, page_obj, num_links, page_kwarg):
        self.nodelist = nodelist
        self.page_obj = template.Variable(page_obj)
        self.num_links = num_links
        self.page_kwarg = page_kwarg

    def render(self, context):

        request = context['request']
        if len(request.GET) > 0:
            qs = request.GET.copy()
            if self.page_kwarg in qs:
                qs.pop(self.page_kwarg)
            query = qs.urlencode()
        else:
            query = ''

        page_obj = self.page_obj.resolve(context)
        paginator = make_paginator(page_obj, self.num_links)
        context.update({
            'paging_first': paginator.first,
            'paging_prev': paginator.prev,
            'paging_pages': paginator.pages,
            'paging_next': paginator.next,
            'paging_last': paginator.last,
            'paging_query': query,
        })

        return self.nodelist.render(context)
