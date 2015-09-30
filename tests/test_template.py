import string
from django.http import HttpRequest
from django.template import Context, Template, TemplateSyntaxError, VariableDoesNotExist
import pytest

from .test_pagination import paginator


FORMAT_STRING = string.Template('''
{% load pagination_tags %}
{% paginate $args %}
    {% for page in paging.pages %}{{ page.number }}{% endfor %}
    {{ paging.query }}
{% endpaginate %}
''')


def test_pagination_without_query():
    template_string = FORMAT_STRING.substitute(args='page_obj 5')

    request = HttpRequest()

    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })

    response = tpl.render(ctx)
    assert '12345' in response


def test_pagination_with_query_without_page_kwarg():
    template_string = FORMAT_STRING.substitute(args='page_obj 5')

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
    template_string = FORMAT_STRING.substitute(args="page_obj 5 'page'")

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
    template_string = FORMAT_STRING.substitute(args='page_obj num_links')

    request = HttpRequest()
    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
        'num_links': 5,
    })

    response = tpl.render(ctx)
    assert '12345' in response


def test_pagination_without_request_should_not_generate_querystring():
    template_string = FORMAT_STRING.substitute(args="page_obj 5 'page'")

    request = HttpRequest()
    request.GET.update({
        'page': '2',
        'term1': 'param1',
        'term2': 'param2',
    })

    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
    })

    response = tpl.render(ctx)
    assert 'term1=param1' not in response
    assert 'term2=param2' not in response


def test_pagination_without_args_should_fail():
    template_string = FORMAT_STRING.substitute(args='')

    with pytest.raises(TemplateSyntaxError):
        Template(template_string)


def test_pagination_without_num_links_should_fail():
    template_string = FORMAT_STRING.substitute(args='page_obj')

    with pytest.raises(TemplateSyntaxError):
        Template(template_string)


def test_pagination_with_too_many_args_should_fail():
    template_string = FORMAT_STRING.substitute(args='page_obj arg2 arg3 arg4')

    with pytest.raises(TemplateSyntaxError):
        Template(template_string)


def test_pagination_with_non_existent_variable():
    template_string = FORMAT_STRING.substitute(args='page_obj does_not_exist')

    request = HttpRequest()

    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })

    with pytest.raises(VariableDoesNotExist):
        tpl.render(ctx)


def test_pagination_with_wrong_page_obj_should_fail():
    template_string = FORMAT_STRING.substitute(args='page_obj 5')

    request = HttpRequest()

    tpl = Template(template_string)
    ctx = Context({
        'page_obj': request,
        'request': request,
    })

    with pytest.raises(TemplateSyntaxError):
        tpl.render(ctx)


def test_pagination_with_str_num_links_should_fail():
    template_string = FORMAT_STRING.substitute(args="page_obj 'abc'")

    request = HttpRequest()

    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })

    with pytest.raises(TemplateSyntaxError):
        tpl.render(ctx)


def test_pagination_with_non_int_num_links_should_fail():
    template_string = FORMAT_STRING.substitute(args='page_obj 2.5')

    request = HttpRequest()

    tpl = Template(template_string)
    ctx = Context({
        'page_obj': paginator.page(1),
        'request': request,
    })

    with pytest.raises(TemplateSyntaxError):
        tpl.render(ctx)
