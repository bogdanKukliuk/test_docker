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

from .. import factories as f
from ..utils import disconnect_signals, reconnect_signals


def setup_module():
    disconnect_signals()


def teardown_module():
    reconnect_signals()


pytestmark = pytest.mark.django_db


def test_project_update_role_points():
    """Test that relation to project roles are created for stories not related to those roles.

    The "relation" is just a mere `RolePoints` relation between the story and the role with
    points set to the project's null-point.
    """
    project = f.ProjectFactory.create()
    related_role = f.RoleFactory.create(project=project, computable=True)
    null_points = f.PointsFactory.create(project=project, value=None)
    user_story = f.UserStoryFactory(project=project)

    new_related_role = f.RoleFactory.create(project=project, computable=True)

    assert user_story.role_points.count() == 1
    assert user_story.role_points.filter(role=new_related_role, points=null_points).count() == 0

    project.update_role_points()

    assert user_story.role_points.count() == 2
    assert user_story.role_points.filter(role=new_related_role, points=null_points).count() == 1
