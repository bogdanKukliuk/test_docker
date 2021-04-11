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
import io
from .. import factories as f

from taiga.base.utils import json
from taiga.export_import.services import render_project

pytestmark = pytest.mark.django_db(transaction=True)


def test_export_issue_finish_date(client):
    issue = f.IssueFactory.create(finished_date="2014-10-22T00:00:00+0000")
    output = io.BytesIO()
    render_project(issue.project, output)
    project_data = json.loads(output.getvalue())
    finish_date = project_data["issues"][0]["finished_date"]
    assert finish_date == "2014-10-22T00:00:00+0000"


def test_export_user_story_finish_date(client):
    user_story = f.UserStoryFactory.create(finish_date="2014-10-22T00:00:00+0000")
    output = io.BytesIO()
    render_project(user_story.project, output)
    project_data = json.loads(output.getvalue())
    finish_date = project_data["user_stories"][0]["finish_date"]
    assert finish_date == "2014-10-22T00:00:00+0000"


def test_export_epic_with_user_stories(client):
    epic = f.EpicFactory.create(subject="test epic export")
    user_story = f.UserStoryFactory.create(project=epic.project)
    f.RelatedUserStory.create(epic=epic, user_story=user_story)
    output = io.BytesIO()
    render_project(user_story.project, output)
    project_data = json.loads(output.getvalue())
    assert project_data["epics"][0]["subject"] == "test epic export"
    assert len(project_data["epics"]) == 1

    assert project_data["epics"][0]["related_user_stories"][0]["user_story"] == user_story.ref
    assert len(project_data["epics"][0]["related_user_stories"]) == 1
