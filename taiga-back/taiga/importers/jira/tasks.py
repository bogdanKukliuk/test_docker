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

import logging
import sys

from django.utils.translation import ugettext as _

from taiga.base.mails import mail_builder
from taiga.users.models import User
from taiga.celery import app
from .normal import JiraNormalImporter
from .agile import JiraAgileImporter

logger = logging.getLogger('taiga.importers.jira')


@app.task(bind=True)
def import_project(self, user_id, url, token, project_id, options, importer_type):
    user = User.objects.get(id=user_id)

    if importer_type == "agile":
        importer = JiraAgileImporter(user, url, token)
    else:
        importer = JiraNormalImporter(user, url, token)

    try:
        project = importer.import_project(project_id, options)
    except Exception as e:
        # Error
        ctx = {
            "user": user,
            "error_subject": _("Error importing Jira project"),
            "error_message": _("Error importing Jira project"),
            "project": project_id,
            "exception": e
        }
        email = mail_builder.importer_import_error(user, ctx)
        email.send()
        logger.error('Error importing Jira project %s (by %s)', project_id, user, exc_info=sys.exc_info())
    else:
        ctx = {
            "project": project,
            "user": user,
        }
        email = mail_builder.jira_import_success(user, ctx)
        email.send()
