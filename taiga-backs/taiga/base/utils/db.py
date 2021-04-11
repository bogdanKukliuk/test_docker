# -*- coding: utf-8 -*-
# Copyright (C) 2014-present Taiga Agile LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db import DatabaseError
from django.db import transaction
from django.shortcuts import _get_queryset

from . import functions

import re


def get_object_or_none(klass, *args, **kwargs):
    """
    Uses get() to return an object, or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more
    than one object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def get_typename_for_model_class(model: object, for_concrete_model=True) -> str:
    """
    Get typename for model instance.
    """
    if for_concrete_model:
        model = model._meta.concrete_model
    else:
        model = model._meta.proxy_for_model

    return "{0}.{1}".format(model._meta.app_label, model._meta.model_name)


def get_typename_for_model_instance(model_instance):
    """
    Get content type tuple from model instance.
    """
    ct = ContentType.objects.get_for_model(model_instance)
    return ".".join([ct.app_label, ct.model])


def reload_attribute(model_instance, attr_name):
    """Fetch the stored value of a model instance attribute.

    :param model_instance: Model instance.
    :param attr_name: Attribute name to fetch.
    """
    qs = type(model_instance).objects.filter(id=model_instance.id)
    return qs.values_list(attr_name, flat=True)[0]


@transaction.atomic
def save_in_bulk(instances, callback=None, precall=None, **save_options):
    """Save a list of model instances.

    :params instances: List of model instances.
    :params callback: Callback to call after each save.
    :params save_options: Additional options to use when saving each instance.
    """
    ret = []
    if callback is None:
        callback = functions.noop

    if precall is None:
        precall = functions.noop

    for instance in instances:
        created = False
        if instance.pk is None:
            created = True

        precall(instance)
        instance.save(**save_options)
        callback(instance, created=created)

    return ret


@transaction.atomic
def update_in_bulk(instances, list_of_new_values, callback=None, precall=None):
    """Update a list of model instances.

    :params instances: List of model instances.
    :params new_values: List of dicts where each dict is the new data corresponding to the instance
    in the same index position as the dict.
    """
    if callback is None:
        callback = functions.noop

    if precall is None:
        precall = functions.noop

    for instance, new_values in zip(instances, list_of_new_values):
        for attribute, value in new_values.items():
            setattr(instance, attribute, value)
        precall(instance)
        instance.save()
        callback(instance)


@transaction.atomic
def update_attr_in_bulk_for_ids(values, attr, model):
    """Update a table using a list of ids.

    :params values: Dict of new values where the key is the pk of the element to update.
    :params attr: attr to update
    :params model: Model of the ids.
    """
    if not values:
        return

    values = [str((id, order)) for id, order in values.items()]
    sql = """
        UPDATE "{tbl}"
        SET "{attr}"=update_values.column2
        FROM (
          VALUES
            {values}
        ) AS update_values
        WHERE "{tbl}"."id"=update_values.column1;
    """.format(tbl=model._meta.db_table,
               values=', '.join(values),
               attr=attr)

    cursor = connection.cursor()

    # We can have deadlocks with multiple updates over the same object
    # In that situation we just retry
    import time
    ts = time.time()
    def trace_info(retries):
        return '/* query=update_attr_in_bulk id={ts} retries={retries} */'.format(retries=retries, ts=ts)

    def _run_sql(retries=0, max_retries=3):
        try:
            cursor.execute(trace_info(retries) + sql)
        except DatabaseError:
            if retries < max_retries:
                _run_sql(retries + 1)

    transaction.on_commit(_run_sql)


def to_tsquery(term):
    """
    Based on: https://gist.github.com/wolever/1a5ccf6396f00229b2dc
    Escape a query string so it's safe to use with Postgres'
    ``to_tsquery(...)``. Single quotes are ignored, double quoted strings
    are used as literals, and the logical operators 'and', 'or', 'not',
    '(', and ')' can be used:
        >>> tsquery_escape("Hello")
        "'hello':*"
        >>> tsquery_escape('"Quoted string"')
        "'quoted string'"
        >>> tsquery_escape("multiple terms OR another")
        "'multiple':* & 'terms':* | 'another':*"
        >>> tsquery_escape("'\"*|"")
        "'\"*|':*"
        >>> tsquery_escape('not foo and (bar or "baz")')
        "! 'foo':* & ( 'bar':* | 'baz' )"
    """

    magic_terms = {
        "and": "&",
        "or": "|",
        "not": "!",
        "OR": "|",
        "AND": "&",
        "NOT": "!",
        "(": "(",
        ")": ")",
    }
    magic_values = set(magic_terms.values())
    paren_count = 0
    res = []
    bits = re.split(r'((?:".*?")|[()])', term)
    for bit in bits:
        if not bit:
            continue
        split_bits = (
            [bit] if bit.startswith('"') and bit.endswith('"') else
            bit.strip().split()
        )
        for bit in split_bits:
            if not bit:
                continue
            if bit in magic_terms:
                bit = magic_terms[bit]
                last = res and res[-1] or ""

                if bit == ")":
                    if last == "(":
                        paren_count -= 1
                        res.pop()
                        continue
                    if paren_count == 0:
                        continue
                    if last in magic_values and last != "(":
                        res.pop()
                elif bit == "|" and last == "&":
                    res.pop()
                elif bit == "!":
                    pass
                elif bit == "(":
                    pass
                elif last in magic_values or not last:
                    continue

                if bit == ")":
                    paren_count -= 1
                elif bit == "(":
                    paren_count += 1

                res.append(bit)
                if bit == ")":
                    res.append("&")
                continue

            bit = bit.replace("'", "")
            bit = bit.replace("\\", "")
            if not bit:
                continue

            if bit.startswith('"') and bit.endswith('"') and len(bit) > 2:
                res.append(bit.replace('"', "'"))
            else:
                res.append("'%s':*" % (bit.replace("'", ""), ))

            res.append("&")

    while res and res[-1] in magic_values:
        last = res[-1]
        if last == ")":
            break
        if last == "(":
            paren_count -= 1
        res.pop()
    while paren_count > 0:
        res.append(")")
        paren_count -= 1

    return " ".join(res)
