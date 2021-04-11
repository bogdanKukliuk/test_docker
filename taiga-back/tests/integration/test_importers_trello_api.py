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
import json

from unittest import mock

from django.urls import reverse

from .. import factories as f
from taiga.base.utils import json
from taiga.base import exceptions as exc


pytestmark = pytest.mark.django_db


def test_auth_url(client):
    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-auth-url")

    with mock.patch('taiga.importers.trello.importer.OAuth1Session') as OAuth1SessionMock:
        session = mock.Mock()
        session.fetch_request_token.return_value = {"oauth_token": "token", "oauth_token_secret": "token"}
        OAuth1SessionMock.return_value = session

        response = client.get(url, content_type="application/json")

    assert response.status_code == 200
    assert 'url' in response.data
    assert response.data['url'] == "https://trello.com/1/OAuthAuthorizeToken?oauth_token=token&scope=read,write,account&expiration=1day&name=Taiga&return_url=http://localhost:9001/project/new/import/trello"


def test_authorize(client):
    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-auth-url")
    authorize_url = reverse("importers-trello-authorize")

    with mock.patch('taiga.importers.trello.importer.OAuth1Session') as OAuth1SessionMock:
        session = mock.Mock()
        session.fetch_request_token.return_value = {"oauth_token": "token", "oauth_token_secret": "token"}
        session.fetch_access_token.return_value = {"oauth_token": "token", "oauth_token_secret": "token"}
        OAuth1SessionMock.return_value = session

        client.get(url, content_type="application/json")
        response = client.post(authorize_url, content_type="application/json", data=json.dumps({"oauth_verifier": "token"}))

    assert response.status_code == 200
    assert 'token' in response.data
    assert response.data['token'] == "token"

def test_authorize_without_token_and_secret(client):
    user = f.UserFactory.create()
    client.login(user)

    authorize_url = reverse("importers-trello-authorize")

    with mock.patch('taiga.importers.trello.importer.OAuth1Session') as OAuth1SessionMock:
        session = mock.Mock()
        session.fetch_access_token.return_value = {"oauth_token": "token", "oauth_token_secret": "token"}
        OAuth1SessionMock.return_value = session

        response = client.post(authorize_url, content_type="application/json", data=json.dumps({"oauth_verifier": "token"}))

    assert response.status_code == 400
    assert 'token' not in response.data


def test_authorize_with_bad_verify(client):
    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-auth-url")
    authorize_url = reverse("importers-trello-authorize")

    with mock.patch('taiga.importers.trello.importer.OAuth1Session') as OAuth1SessionMock:
        session = mock.Mock()
        session.fetch_request_token.return_value = {"oauth_token": "token", "oauth_token_secret": "token"}
        session.fetch_access_token.side_effect = Exception("Bad Token")
        OAuth1SessionMock.return_value = session

        client.get(url, content_type="application/json")
        response = client.post(authorize_url, content_type="application/json", data=json.dumps({"oauth_verifier": "token"}))

    assert response.status_code == 400
    assert 'token' not in response.data


def test_import_trello_list_users(client, settings):
    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-list-users")

    with mock.patch('taiga.importers.trello.api.TrelloImporter') as TrelloImporterMock:
        instance = mock.Mock()
        instance.list_users.return_value = [
            {"id": 1, "fullName": "user1", "email": None},
            {"id": 2, "fullName": "user2", "email": None}
        ]
        TrelloImporterMock.return_value = instance
        response = client.post(url, content_type="application/json", data=json.dumps({"token": "token", "project": 1}))

    assert response.status_code == 200
    assert response.data[0]["id"] == 1
    assert response.data[1]["id"] == 2


def test_import_trello_list_users_without_project(client, settings):
    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-list-users")

    with mock.patch('taiga.importers.trello.api.TrelloImporter') as TrelloImporterMock:
        instance = mock.Mock()
        instance.list_users.return_value = [
            {"id": 1, "fullName": "user1", "email": None},
            {"id": 2, "fullName": "user2", "email": None}
        ]
        TrelloImporterMock.return_value = instance
        response = client.post(url, content_type="application/json", data=json.dumps({"token": "token"}))

    assert response.status_code == 400


def test_import_trello_list_users_with_problem_on_request(client, settings):
    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-list-users")

    with mock.patch('taiga.importers.trello.importer.TrelloClient') as TrelloClientMock:
        instance = mock.Mock()
        instance.get.side_effect = exc.WrongArguments("Invalid Request")
        TrelloClientMock.return_value = instance
        response = client.post(url, content_type="application/json", data=json.dumps({"token": "token", "project": 1}))

    assert response.status_code == 400


def test_import_trello_list_projects(client, settings):
    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-list-projects")

    with mock.patch('taiga.importers.trello.api.TrelloImporter') as TrelloImporterMock:
        instance = mock.Mock()
        instance.list_projects.return_value = ["project1", "project2"]
        TrelloImporterMock.return_value = instance
        response = client.post(url, content_type="application/json", data=json.dumps({"token": "token"}))

    assert response.status_code == 200
    assert response.data[0] == "project1"
    assert response.data[1] == "project2"


def test_import_trello_list_projects_with_problem_on_request(client, settings):
    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-list-projects")

    with mock.patch('taiga.importers.trello.importer.TrelloClient') as TrelloClientMock:
        instance = mock.Mock()
        instance.get.side_effect = exc.WrongArguments("Invalid Request")
        TrelloClientMock.return_value = instance
        response = client.post(url, content_type="application/json", data=json.dumps({"token": "token"}))

    assert response.status_code == 400


def test_import_trello_project_without_project_id(client, settings):
    settings.CELERY_ENABLED = True

    user = f.UserFactory.create()
    client.login(user)

    url = reverse("importers-trello-import-project")

    with mock.patch('taiga.importers.trello.tasks.TrelloImporter') as TrelloImporterMock:
        response = client.post(url, content_type="application/json", data=json.dumps({"token": "token"}))

    assert response.status_code == 400
    settings.CELERY_ENABLED = False


def test_import_trello_project_with_celery_enabled(client, settings):
    settings.CELERY_ENABLED = True

    user = f.UserFactory.create()
    project = f.ProjectFactory.create(slug="async-imported-project")
    client.login(user)

    url = reverse("importers-trello-import-project")

    with mock.patch('taiga.importers.trello.tasks.TrelloImporter') as TrelloImporterMock:
        instance = mock.Mock()
        instance.import_project.return_value = project
        TrelloImporterMock.return_value = instance
        response = client.post(url, content_type="application/json", data=json.dumps({"token": "token", "project": 1}))

    assert response.status_code == 202
    assert "task_id" in response.data
    settings.CELERY_ENABLED = False


def test_import_trello_project_with_celery_disabled(client, settings):
    user = f.UserFactory.create()
    project = f.ProjectFactory.create(slug="imported-project")
    client.login(user)

    url = reverse("importers-trello-import-project")

    with mock.patch('taiga.importers.trello.api.TrelloImporter') as TrelloImporterMock:
        instance = mock.Mock()
        instance.import_project.return_value = project
        TrelloImporterMock.return_value = instance
        response = client.post(url, content_type="application/json", data=json.dumps({"token": "token", "project": 1}))

    assert response.status_code == 200
    assert "slug" in response.data
    assert response.data['slug'] == "imported-project"
