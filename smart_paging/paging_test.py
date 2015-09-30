from django.core.paginator import Paginator
import pytest
from smart_paging.templatetags.paging_tags import make_paginator

even_num_links = 6
odd_num_links = 5

testargs = 'num_links, num_page, first_link, last_link, current_index'
testdata = [
    (odd_num_links, 1, 1, 5, 0),
    (odd_num_links, 2, 1, 5, 1),
    (odd_num_links, 3, 1, 5, 2),
    (odd_num_links, 4, 2, 6, 2),
    (odd_num_links, 5, 3, 7, 2),
    (odd_num_links, 6, 4, 8, 2),
    (odd_num_links, 7, 5, 9, 2),
    (odd_num_links, 8, 6, 10, 2),
    (odd_num_links, 9, 6, 10, 3),
    (odd_num_links, 10, 6, 10, 4),

    (even_num_links, 1, 1, 6, 0),
    (even_num_links, 2, 1, 6, 1),
    (even_num_links, 3, 1, 6, 2),
    (even_num_links, 4, 2, 7, 2),
    (even_num_links, 5, 3, 8, 2),
    (even_num_links, 6, 4, 9, 2),
    (even_num_links, 7, 5, 10, 2),
    (even_num_links, 8, 5, 10, 3),
    (even_num_links, 9, 5, 10, 4),
    (even_num_links, 10, 5, 10, 5),
]

paginator = Paginator(range(1, 51), 5)


@pytest.mark.parametrize(testargs, testdata)
def test_paginator_links(num_links, num_page, first_link, last_link, current_index):
    page = paginator.page(num_page)

    paging = make_paginator(page, num_links)

    current = None

    for i, page in enumerate(paging.pages):
        if page.is_current:
            current = i

    assert current is not None, 'Missing current page'

    assert paging.pages[0].number == first_link, 'first link was {}'.format(paging.pages[0].number)
    assert paging.pages[-1].number == last_link, 'last link was {}'.format(paging.pages[-1].number)
    assert paging.pages[current_index].is_current, 'current was {}'.format(current)
