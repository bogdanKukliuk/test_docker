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

from django.urls import reverse

from tests import factories as f
from tests.utils import helper_test_http_method

from taiga.base.utils import json

import pytest
pytestmark = pytest.mark.django_db


@pytest.fixture
def data():
    m = type("Models", (object,), {})
    m.user = f.UserFactory.create()
    m.project = f.ProjectFactory.create(is_private=False)
    f.MembershipFactory(user=m.project.owner, project=m.project, is_admin=True)

    return m


def test_contact_create(client, data):
    url = reverse("contact-list")
    users = [None, data.user]

    contact_data = json.dumps({
        "project": data.project.id,
        "comment": "Testing comment"
    })
    results = helper_test_http_method(client, 'post', url, contact_data, users)
    assert results == [401, 201]
