=======================
django-smart-pagination
=======================

Generate pagination links for Django

Instead of displaying links to all the pages at once, django-smart-pagination calculates a limited subset of them.

Works with Django Templates and Jinja2.

-----
Usage
-----

Use a pagination block passing the ``Page`` object, the number of links (literal of variable)
and the name to associate the ``smart_pagination.Paginator`` object.

.. code-block:: django

    {% load pagination_tags %}
    {% paginate page_obj num_links paging %}
    <ul>
        {% for page in paging.pages %}
        <li class="{% if page.is_current %}current{% endif %}">{{ page.number }}</li>
        {% endfor %}
    </ul>
    {% endpaginate %}

The ``Paginator`` object contains the following properties:

===== =================================================================
first First ``Page``. Will be ``None`` if it is already the first page.
prev  Previous ``Page``. Will be ``None`` if there is no previous page.
pages List of pages.
next  Next ``Page``. Will be ``None`` if there is no next page.
last  Last ``Page``. Will be ``None`` if it is already the last page.
===== =================================================================

.. code-block:: django

    {% load pagination_tags %}
    {% paginate page_obj num_links paging %}
    <ul>
        {% if paging.first %}
        <li>First - {{ paging.first.number }}</li>
        {% endif %}

        {% if paging.prev %}
        <li>Previous - {{ paging.prev.number }}</li>
        {% endif %}

        {% for page in paging.pages %}
        <li class="{% if page.is_current %}current{% endif %}">{{ page.number }}</li>
        {% endfor %}

        {% if paging.next %}
        <li>Next - {{ paging.next.number }}</li>
        {% endif %}

        {% if paging.last %}
        <li>Last - {{ paging.last.number }}</li>
        {% endif %}
    </ul>
    {% endpaginate %}

If you are sending the page_kwarg as a query parameter, you can optionally pass a fourth argument with the name
of the page_kwarg and the ``Paginator`` will provide the query string without the page_kwarg:

.. code-block:: django

    {% load pagination_tags %}
    {% paginate page_obj num_links paging 'page' %}
    <ul>
        {% for page in paging.pages %}
        <li><a href="?page={{ page.number }}&{{ paging.query }}">{{ page.number }}</a></li>
        {% endfor %}
    </ul>
    {% endpaginate %}