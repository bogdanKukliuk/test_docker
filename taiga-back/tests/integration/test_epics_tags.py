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

from unittest import mock
from collections import OrderedDict

from django.urls import reverse

from taiga.base.utils import json

from .. import factories as f

import pytest
pytestmark = pytest.mark.django_db


def test_api_epic_add_new_tags_with_error(client):
    project = f.ProjectFactory.create()
    epic = f.create_epic(project=project, status__project=project)
    f.MembershipFactory.create(project=project, user=epic.owner, is_admin=True)
    url = reverse("epics-detail", kwargs={"pk": epic.pk})
    data = {
        "tags": [],
        "version": epic.version
    }

    client.login(epic.owner)

    data["tags"] = [1]
    response = client.json.patch(url, json.dumps(data))
    assert response.status_code == 400, response.data
    assert "tags" in response.data

    data["tags"] = [["back"]]
    response = client.json.patch(url, json.dumps(data))
    assert response.status_code == 400, response.data
    assert "tags" in response.data

    data["tags"] = [["back", "#cccc"]]
    response = client.json.patch(url, json.dumps(data))
    assert response.status_code == 400, response.data
    assert "tags" in response.data

    data["tags"] = [[1, "#ccc"]]
    response = client.json.patch(url, json.dumps(data))
    assert response.status_code == 400, response.data
    assert "tags" in response.data


def test_api_epic_add_new_tags_without_colors(client):
    project = f.ProjectFactory.create()
    epic = f.create_epic(project=project, status__project=project)
    f.MembershipFactory.create(project=project, user=epic.owner, is_admin=True)
    url = reverse("epics-detail", kwargs={"pk": epic.pk})
    data = {
        "tags": [
            ["back", None],
            ["front", None],
            ["ux", None]
        ],
        "version": epic.version
    }

    client.login(epic.owner)

    response = client.json.patch(url, json.dumps(data))

    assert response.status_code == 200, response.data

    tags_colors = OrderedDict(project.tags_colors)
    assert not tags_colors.keys()

    project.refresh_from_db()

    tags_colors = OrderedDict(project.tags_colors)
    assert "back" in tags_colors and "front" in tags_colors and "ux" in tags_colors


def test_api_epic_add_new_tags_with_colors(client):
    project = f.ProjectFactory.create()
    epic = f.create_epic(project=project, status__project=project)
    f.MembershipFactory.create(project=project, user=epic.owner, is_admin=True)
    url = reverse("epics-detail", kwargs={"pk": epic.pk})
    data = {
        "tags": [
            ["back", "#fff8e7"],
            ["front", None],
            ["ux", "#fabada"]
        ],
        "version": epic.version
    }

    client.login(epic.owner)

    response = client.json.patch(url, json.dumps(data))
    assert response.status_code == 200, response.data

    tags_colors = OrderedDict(project.tags_colors)
    assert not tags_colors.keys()

    project.refresh_from_db()

    tags_colors = OrderedDict(project.tags_colors)
    assert "back" in tags_colors and "front" in tags_colors and "ux" in tags_colors
    assert tags_colors["back"] == "#fff8e7"
    assert tags_colors["ux"] == "#fabada"


def test_api_create_new_epic_with_tags(client):
    project = f.ProjectFactory.create(tags_colors=[["front", "#aaaaaa"], ["ux", "#fabada"]])
    status = f.EpicStatusFactory.create(project=project)
    project.default_epic_status = status
    project.save()
    f.MembershipFactory.create(project=project, user=project.owner, is_admin=True)
    url = reverse("epics-list")

    data = {
        "subject": "Test user story",
        "project": project.id,
        "tags": [
            ["back", "#fff8e7"],
            ["front", None],
            ["ux", "#fabada"]
        ]
    }

    client.login(project.owner)

    response = client.json.post(url, json.dumps(data))
    assert response.status_code == 201, response.data

    epic_tags_colors = OrderedDict(response.data["tags"])

    assert epic_tags_colors["back"] == "#fff8e7"
    assert epic_tags_colors["front"] == "#aaaaaa"
    assert epic_tags_colors["ux"] == "#fabada"

    tags_colors = OrderedDict(project.tags_colors)

    project.refresh_from_db()

    tags_colors = OrderedDict(project.tags_colors)
    assert tags_colors["back"] == "#fff8e7"
    assert tags_colors["ux"] == "#fabada"
    assert tags_colors["front"] == "#aaaaaa"
