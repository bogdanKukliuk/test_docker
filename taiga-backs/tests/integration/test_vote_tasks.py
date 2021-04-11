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
from django.urls import reverse

from .. import factories as f

pytestmark = pytest.mark.django_db


def test_upvote_task(client):
    user = f.UserFactory.create()
    task = f.create_task(owner=user, milestone=None)
    f.MembershipFactory.create(project=task.project, user=user, is_admin=True)
    url = reverse("tasks-upvote", args=(task.id,))

    client.login(user)
    response = client.post(url)

    assert response.status_code == 200


def test_downvote_task(client):
    user = f.UserFactory.create()
    task = f.create_task(owner=user, milestone=None)
    f.MembershipFactory.create(project=task.project, user=user, is_admin=True)
    url = reverse("tasks-downvote", args=(task.id,))

    client.login(user)
    response = client.post(url)

    assert response.status_code == 200


def test_list_task_voters(client):
    user = f.UserFactory.create()
    task = f.create_task(owner=user)
    f.MembershipFactory.create(project=task.project, user=user, is_admin=True)
    f.VoteFactory.create(content_object=task, user=user)
    url = reverse("task-voters-list", args=(task.id,))

    client.login(user)
    response = client.get(url)

    assert response.status_code == 200
    assert response.data[0]['id'] == user.id


def test_get_task_voter(client):
    user = f.UserFactory.create()
    task = f.create_task(owner=user)
    f.MembershipFactory.create(project=task.project, user=user, is_admin=True)
    vote = f.VoteFactory.create(content_object=task, user=user)
    url = reverse("task-voters-detail", args=(task.id, vote.user.id))

    client.login(user)
    response = client.get(url)

    assert response.status_code == 200
    assert response.data['id'] == vote.user.id


def test_get_task_votes(client):
    user = f.UserFactory.create()
    task = f.create_task(owner=user)
    f.MembershipFactory.create(project=task.project, user=user, is_admin=True)
    url = reverse("tasks-detail", args=(task.id,))

    f.VotesFactory.create(content_object=task, count=5)

    client.login(user)
    response = client.get(url)

    assert response.status_code == 200
    assert response.data['total_voters'] == 5


def test_get_task_is_voted(client):
    user = f.UserFactory.create()
    task = f.create_task(owner=user, milestone=None)
    f.MembershipFactory.create(project=task.project, user=user, is_admin=True)
    f.VotesFactory.create(content_object=task)
    url_detail = reverse("tasks-detail", args=(task.id,))
    url_upvote = reverse("tasks-upvote", args=(task.id,))
    url_downvote = reverse("tasks-downvote", args=(task.id,))

    client.login(user)

    response = client.get(url_detail)
    assert response.status_code == 200
    assert response.data['total_voters'] == 0
    assert response.data['is_voter'] == False

    response = client.post(url_upvote)
    assert response.status_code == 200

    response = client.get(url_detail)
    assert response.status_code == 200
    assert response.data['total_voters'] == 1
    assert response.data['is_voter'] == True

    response = client.post(url_downvote)
    assert response.status_code == 200

    response = client.get(url_detail)
    assert response.status_code == 200
    assert response.data['total_voters'] == 0
    assert response.data['is_voter'] == False
