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

from django.conf import settings

from taiga.base import response
from taiga.base.api.viewsets import ReadOnlyListViewSet

from . import permissions


class LocalesViewSet(ReadOnlyListViewSet):
    permission_classes = (permissions.LocalesPermission,)

    def list(self, request, *args, **kwargs):
        locales = [{"code": c, "name": n, "bidi": c in settings.LANGUAGES_BIDI} for c, n in settings.LANGUAGES]
        return response.Ok(locales)
