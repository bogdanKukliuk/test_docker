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

from taiga.users.models import Role
from taiga.projects.models import Membership
from taiga.projects.models import Project

from .. import factories as f


pytestmark = pytest.mark.django_db


def test_destroy_role_and_reassign_members(client):
    user1 = f.UserFactory.create()
    user2 = f.UserFactory.create()
    project = f.ProjectFactory.create(owner=user1)
    role1 = f.RoleFactory.create(project=project)
    role2 = f.RoleFactory.create(project=project)
    f.MembershipFactory.create(project=project, user=user1, role=role1, is_admin=True)
    f.MembershipFactory.create(project=project, user=user2, role=role2)

    url = reverse("roles-detail", args=[role2.pk]) + "?moveTo={}".format(role1.pk)

    client.login(user1)

    response = client.delete(url)
    assert response.status_code == 204

    qs = Role.objects.filter(project=project)
    assert qs.count() == 1

    qs = Membership.objects.filter(project=project, role_id=role2.pk)
    assert qs.count() == 0

    qs = Membership.objects.filter(project=project, role_id=role1.pk)
    assert qs.count() == 2
