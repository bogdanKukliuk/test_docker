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

from django.apps import apps


def attach_total_voters_to_queryset(queryset, as_field="total_voters"):
    """Attach votes count to each object of the queryset.

    Because of laziness of vote objects creation, this makes much simpler and more efficient to
    access to voted-object number of votes.

    (The other way was to do it in the serializer with some try/except blocks and additional
    queries)

    :param queryset: A Django queryset object.
    :param as_field: Attach the votes-count as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(model)
    sql = """SELECT coalesce(SUM(total_voters), 0) FROM (
                SELECT coalesce(votes_votes.count, 0) total_voters
                  FROM votes_votes
                 WHERE votes_votes.content_type_id = {type_id}
                   AND votes_votes.object_id = {tbl}.id
          ) as e"""

    sql = sql.format(type_id=type.id, tbl=model._meta.db_table)
    qs = queryset.extra(select={as_field: sql})
    return qs


def attach_is_voter_to_queryset(queryset, user, as_field="is_voter"):
    """Attach is_vote boolean to each object of the queryset.

    Because of laziness of vote objects creation, this makes much simpler and more efficient to
    access to votes-object and check if the curren user vote it.

    (The other way was to do it in the serializer with some try/except blocks and additional
    queries)

    :param queryset: A Django queryset object.
    :param user: A users.User object model
    :param as_field: Attach the boolean as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(model)
    if user is None or user.is_anonymous:
        sql = """SELECT false"""
    else:
        sql = ("""SELECT CASE WHEN (SELECT count(*)
                                      FROM votes_vote
                                     WHERE votes_vote.content_type_id = {type_id}
                                       AND votes_vote.object_id = {tbl}.id
                                       AND votes_vote.user_id = {user_id}) > 0
                              THEN TRUE
                              ELSE FALSE
                         END""")
        sql = sql.format(type_id=type.id, tbl=model._meta.db_table, user_id=user.id)

    qs = queryset.extra(select={as_field: sql})
    return qs
