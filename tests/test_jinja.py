import string
from django.http import HttpRequest
from jinja2 import Environment, TemplateSyntaxError, TemplateError
import pytest

from smart_pagination.templatetags.pagination_jinja import PaginationExtension
from .test_pagination import paginator


FORMAT_STRING = string.Template('''
{% paginate $args %}
    {% for page in paging.pages %}{{ page.number }}{% endfor %}
    {{ paging.query }}
{% endpaginate %}
''')

env = Environment(extensions=[PaginationExtension])


def test_pagination_without_query():
    template_string = FORMAT_STRING.substitute(args="page_obj, 5, 'paging'")

    request = HttpRequest()

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': paginator.page(1),
        'request': request,
    }

    response = tpl.render(**ctx)
    assert '12345' in response


def test_pagination_with_query_without_page_kwarg():
    template_string = FORMAT_STRING.substitute(args="page_obj, 5, 'paging'")

    request = HttpRequest()
    request.GET.update({
        'term1': 'param1',
        'term2': 'param2',
    })

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': paginator.page(1),
        'request': request,
    }

    response = tpl.render(**ctx)
    assert '12345' in response
    assert 'term1=param1' not in response
    assert 'term2=param2' not in response


def test_pagination_with_query_and_page_kwarg():
    template_string = FORMAT_STRING.substitute(args="page_obj, 5, 'paging', 'page'")

    request = HttpRequest()
    request.GET.update({
        'page': '2',
        'term1': 'param1',
        'term2': 'param2',
    })

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': paginator.page(1),
        'request': request,
    }

    response = tpl.render(**ctx)
    assert '12345' in response
    assert 'term1=param1' in response
    assert 'term2=param2' in response
    assert 'page=2' not in response


def test_pagination_with_num_links_variable():
    template_string = FORMAT_STRING.substitute(args="page_obj, num_links, 'paging'")

    request = HttpRequest()

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': paginator.page(1),
        'request': request,
        'num_links': 5,
    }

    response = tpl.render(**ctx)
    assert '12345' in response


def test_pagination_without_request_should_not_generate_querystring():
    template_string = FORMAT_STRING.substitute(args="page_obj, 5, 'paging', 'page'")

    request = HttpRequest()
    request.GET.update({
        'page': '2',
        'term1': 'param1',
        'term2': 'param2',
    })

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': paginator.page(1),
    }

    response = tpl.render(**ctx)
    assert 'term1=param1' not in response
    assert 'term2=param2' not in response


def test_pagination_without_args_should_fail():
    template_string = FORMAT_STRING.substitute(args='')

    with pytest.raises(TemplateSyntaxError):
        env.from_string(template_string)


def test_pagination_without_num_links_should_fail():
    template_string = FORMAT_STRING.substitute(args='page_obj')

    with pytest.raises(TemplateSyntaxError):
        env.from_string(template_string)


def test_pagination_without_var_name_should_fail():
    template_string = FORMAT_STRING.substitute(args='page_obj, 5')

    with pytest.raises(TemplateSyntaxError):
        env.from_string(template_string)


def test_pagination_with_too_many_args_should_fail():
    template_string = FORMAT_STRING.substitute(args='page_obj, arg2, arg3, arg4, arg5')

    with pytest.raises(TemplateSyntaxError):
        env.from_string(template_string)


def test_pagination_with_non_existent_variable():
    template_string = FORMAT_STRING.substitute(args="page_obj, does_not_exist, 'paging'")

    request = HttpRequest()

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': paginator.page(1),
        'request': request,
    }

    with pytest.raises(TemplateError):
        tpl.render(**ctx)


def test_pagination_with_wrong_page_obj_should_fail():
    template_string = FORMAT_STRING.substitute(args="page_obj, 5, 'paging'")

    request = HttpRequest()

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': request,
        'request': request,
    }

    with pytest.raises(TemplateError):
        tpl.render(**ctx)


def test_pagination_with_str_num_links_should_fail():
    template_string = FORMAT_STRING.substitute(args="page_obj, 'abc', 'paging'")

    request = HttpRequest()

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': paginator.page(1),
        'request': request,
    }

    with pytest.raises(TemplateError):
        tpl.render(**ctx)


def test_pagination_with_non_int_num_links_should_fail():
    template_string = FORMAT_STRING.substitute(args="page_obj, 2.5, 'paging'")

    request = HttpRequest()

    tpl = env.from_string(template_string)
    ctx = {
        'page_obj': paginator.page(1),
        'request': request,
    }

    with pytest.raises(TemplateError):
        tpl.render(**ctx)
