from django.http import HttpRequest
from django.template import Context, Template, TemplateSyntaxError, VariableDoesNotExist
import pytest

from .test_paging import paginator


def test_pagination_without_query():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj 5 %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
        {% endpaginate %}
        '''

    request = HttpRequest()
    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })
    response = tpl.render(ctx)
    assert '12345' in response


def test_pagination_with_query_without_page_kwarg():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj 5 %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
            {{ paging_query }}
        {% endpaginate %}
        '''

    request = HttpRequest()
    request.GET.update({
        'term1': 'param1',
        'term2': 'param2',
    })
    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })
    response = tpl.render(ctx)
    assert '12345' in response
    assert 'term1=param1' not in response
    assert 'term2=param2' not in response


def test_pagination_with_query_and_page_kwarg():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj 5 'page' %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
            {{ paging_query }}
        {% endpaginate %}
        '''

    request = HttpRequest()
    request.GET.update({
        'page': '2',
        'term1': 'param1',
        'term2': 'param2',
    })

    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })
    response = tpl.render(ctx)
    assert '12345' in response
    assert 'term1=param1' in response
    assert 'term2=param2' in response
    assert 'page=2' not in response


def test_pagination_without_num_links_variable():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj num_links %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
        {% endpaginate %}
        '''

    request = HttpRequest()
    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
        'num_links': 5,
    })
    response = tpl.render(ctx)
    assert '12345' in response


def test_pagination_without_num_links_should_fail():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
        {% endpaginate %}
        '''

    with pytest.raises(TemplateSyntaxError):
        Template(template_string)


def test_pagination_with_too_many_args_should_fail():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj arg2 arg3 arg4 %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
        {% endpaginate %}
        '''

    with pytest.raises(TemplateSyntaxError):
        Template(template_string)


def test_pagination_with_non_existent_variable():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj dont_exist %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
        {% endpaginate %}
        '''

    request = HttpRequest()
    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })

    with pytest.raises(VariableDoesNotExist):
        tpl.render(ctx)


def test_pagination_with_str_num_links_should_fail():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj 'abc' %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
        {% endpaginate %}
        '''

    request = HttpRequest()
    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })

    with pytest.raises(TemplateSyntaxError):
        tpl.render(ctx)


def test_pagination_with_non_int_num_links_should_fail():
    template_string = '''
        {% load paging_tags %}
        {% paginate page_obj 2.5 %}
            {% for page in paging_pages %}{{ page.number }}{% endfor %}
        {% endpaginate %}
        '''

    request = HttpRequest()
    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })

    with pytest.raises(TemplateSyntaxError):
        tpl.render(ctx)
