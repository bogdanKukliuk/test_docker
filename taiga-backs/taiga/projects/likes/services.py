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

from django.db.models import F
from django.db.transaction import atomic
from django.apps import apps
from django.contrib.auth import get_user_model

from .models import Like


def add_like(obj, user):
    """Add a like to an object.

    If the user has already liked the object nothing happends, so this function can be considered
    idempotent.

    :param obj: Any Django model instance.
    :param user: User adding the like. :class:`~taiga.users.models.User` instance.
    """
    obj_type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(obj)
    with atomic():
        like, created = Like.objects.get_or_create(content_type=obj_type, object_id=obj.id, user=user)
        if like.project is not None:
            like.project.refresh_totals()

    return like


def remove_like(obj, user):
    """Remove an user like from an object.

    If the user has not liked the object nothing happens so this function can be considered
    idempotent.

    :param obj: Any Django model instance.
    :param user: User removing her like. :class:`~taiga.users.models.User` instance.
    """
    obj_type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(obj)
    with atomic():
        qs = Like.objects.filter(content_type=obj_type, object_id=obj.id, user=user)
        if not qs.exists():
            return

        like = qs.first()
        project = like.project
        qs.delete()

        if project is not None:
            project.refresh_totals()


def get_fans(obj):
    """Get the fans of an object.

    :param obj: Any Django model instance.

    :return: User queryset object representing the users that liked the object.
    """
    obj_type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(obj)
    return get_user_model().objects.filter(likes__content_type=obj_type, likes__object_id=obj.id)


def get_liked(user_or_id, model):
    """Get the objects liked by an user.

    :param user_or_id: :class:`~taiga.users.models.User` instance or id.
    :param model: Show only objects of this kind. Can be any Django model class.

    :return: Queryset of objects representing the likes of the user.
    """
    obj_type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(model)
    conditions = ('likes_like.content_type_id = %s',
                  '%s.id = likes_like.object_id' % model._meta.db_table,
                  'likes_like.user_id = %s')

    if isinstance(user_or_id, get_user_model()):
        user_id = user_or_id.id
    else:
        user_id = user_or_id

    return model.objects.extra(where=conditions, tables=('likes_like',),
                               params=(obj_type.id, user_id))
