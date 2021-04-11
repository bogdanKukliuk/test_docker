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

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _


class TaggedMixin(models.Model):
    tags = ArrayField(models.TextField(),
                      null=True, blank=True, default=list, verbose_name=_("tags"))

    class Meta:
        abstract = True


class TagsColorsMixin(models.Model):
    tags_colors = ArrayField(ArrayField(models.TextField(null=True, blank=True), size=2),
                             null=True, blank=True, default=list, verbose_name=_("tags colors"))

    class Meta:
        abstract = True
