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

import pytest
from unittest import mock

from django.urls import reverse
from django.core.cache import cache

from taiga.base.utils import json

from .. import factories as f

pytestmark = pytest.mark.django_db


import_rate_path = "taiga.export_import.throttling.ImportModeRateThrottle.get_rate"


def test_anonimous_throttling_policy(client, settings):
    f.create_project()
    url = reverse("projects-list")
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = "2/min"

    with mock.patch(import_rate_path) as import_rate:
        import_rate.return_value = "7/day"

        cache.clear()
        response = client.json.get(url)
        assert response.status_code == 200
        response = client.json.get(url)
        assert response.status_code == 200
        response = client.json.get(url)
        assert response.status_code == 429

    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None
    cache.clear()


def test_user_throttling_policy(client, settings):
    project = f.create_project()
    f.MembershipFactory.create(project=project, user=project.owner, is_admin=True)
    url = reverse("projects-detail", kwargs={"pk": project.pk})
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = "4/min"

    client.login(project.owner)

    with mock.patch(import_rate_path) as import_rate:
        import_rate.return_value = "7/day"

        cache.clear()
        response = client.json.get(url)
        assert response.status_code == 200
        response = client.json.get(url)
        assert response.status_code == 200
        response = client.json.get(url)
        assert response.status_code == 200
        response = client.json.get(url)
        assert response.status_code == 200
        response = client.json.get(url)
        assert response.status_code == 429

    client.logout()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None
    cache.clear()


def test_import_mode_throttling_policy(client, settings):
    project = f.create_project()
    f.MembershipFactory.create(project=project, user=project.owner, is_admin=True)
    project.default_issue_type = f.IssueTypeFactory.create(project=project)
    project.default_issue_status = f.IssueStatusFactory.create(project=project)
    project.default_severity = f.SeverityFactory.create(project=project)
    project.default_priority = f.PriorityFactory.create(project=project)
    project.save()
    url = reverse("importer-issue", args=[project.pk])
    data = {
        "subject": "Test"
    }
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = "2/min"
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = "4/min"

    client.login(project.owner)

    with mock.patch(import_rate_path) as import_rate:
        import_rate.return_value = "7/day"

        cache.clear()
        response = client.json.post(url, json.dumps(data))
        assert response.status_code == 201
        response = client.json.post(url, json.dumps(data))
        assert response.status_code == 201
        response = client.json.post(url, json.dumps(data))
        assert response.status_code == 201
        response = client.json.post(url, json.dumps(data))
        assert response.status_code == 201
        response = client.json.post(url, json.dumps(data))
        assert response.status_code == 201
        response = client.json.post(url, json.dumps(data))
        assert response.status_code == 201
        response = client.json.post(url, json.dumps(data))
        assert response.status_code == 201
        response = client.json.post(url, json.dumps(data))
        assert response.status_code == 429

    client.logout()

    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None
    cache.clear()
