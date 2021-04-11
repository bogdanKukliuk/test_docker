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

from collections import OrderedDict

from .generics import GenericSitemap

from .projects import ProjectsSitemap
from .projects import ProjectBacklogsSitemap
from .projects import ProjectKanbansSitemap

from .epics import EpicsSitemap

from .milestones import MilestonesSitemap

from .userstories import UserStoriesSitemap

from .tasks import TasksSitemap

from .issues import IssuesSitemap

from .wiki import WikiPagesSitemap

from .users import UsersSitemap


sitemaps = OrderedDict([
    ("generics", GenericSitemap),

    ("projects", ProjectsSitemap),
    ("project-backlogs", ProjectBacklogsSitemap),
    ("project-kanbans", ProjectKanbansSitemap),

    ("epics", EpicsSitemap),

    ("milestones", MilestonesSitemap),

    ("userstories", UserStoriesSitemap),

    ("tasks", TasksSitemap),

    ("issues", IssuesSitemap),

    ("wikipages", WikiPagesSitemap),

    ("users", UsersSitemap)
])
