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

from django.db.models import Q
from django.apps import apps
from datetime import timedelta
from django.utils import timezone

from taiga.front.templatetags.functions import resolve

from .base import Sitemap


class EpicsSitemap(Sitemap):
    def items(self):
        epic_model = apps.get_model("epics", "Epic")

        # Get epics of public projects OR private projects if anon user can view them
        queryset = epic_model.objects.filter(Q(project__is_private=False) |
                                             Q(project__is_private=True,
                                               project__anon_permissions__contains=["view_epics"]))

        queryset = queryset.exclude(description="")
        queryset = queryset.exclude(description__isnull=True)

        # Exclude blocked projects
        queryset = queryset.filter(project__blocked_code__isnull=True)

        # Project data is needed
        queryset = queryset.select_related("project")

        return queryset

    def location(self, obj):
        return resolve("epic", obj.project.slug, obj.ref)

    def lastmod(self, obj):
        return obj.modified_date

    def changefreq(self, obj):
        if (timezone.now() - obj.modified_date) > timedelta(days=90):
            return "monthly"
        return "weekly"

    def priority(self, obj):
        return 0.5
