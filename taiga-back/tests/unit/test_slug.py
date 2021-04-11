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

from django.contrib.auth import get_user_model

from taiga.projects.models import Project
from taiga.base.utils.slug import slugify

import pytest
pytestmark = pytest.mark.django_db(transaction=True)


def test_slugify_1():
    assert slugify("漢字") == "han-zi"


def test_slugify_2():
    assert slugify("TestExamplePage") == "testexamplepage"


def test_slugify_3():
    assert slugify(None) == ""


def test_project_slug_with_special_chars():
    user = get_user_model().objects.create(username="test")
    project = Project.objects.create(name="漢字", description="漢字", owner=user)
    project.save()

    assert project.slug == "test-han-zi"


def test_project_with_existing_name_slug_with_special_chars():
    user = get_user_model().objects.create(username="test")
    Project.objects.create(name="漢字", description="漢字", owner=user)
    project = Project.objects.create(name="漢字", description="漢字", owner=user)

    assert project.slug == "test-han-zi-1"
