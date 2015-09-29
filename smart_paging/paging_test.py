from django.core.paginator import Paginator, Page

from smart_paging.templatetags.paging_tags import get_paginator


def test_paginator():
    paginator = Paginator(range(1, 51), 5)
    page = Page(range(5, 11), 2, paginator)

    paging = get_paginator(page, 3)
    assert not paging.pages[0].is_current
