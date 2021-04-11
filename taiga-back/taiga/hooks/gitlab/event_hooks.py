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

import re
import os

from taiga.hooks.event_hooks import (BaseIssueEventHook, BaseIssueCommentEventHook, BasePushEventHook,
                                     ISSUE_ACTION_CREATE, ISSUE_ACTION_UPDATE, ISSUE_ACTION_CLOSE,
                                     ISSUE_ACTION_REOPEN)


class BaseGitLabEventHook():
    platform = "GitLab"
    platform_slug = "gitlab"

    def replace_gitlab_references(self, project_url, wiki_text):
        if wiki_text is None:
            wiki_text = ""

        template = "\g<1>[GitLab#\g<2>]({}/issues/\g<2>)\g<3>".format(project_url)
        return re.sub(r"(\s|^)#(\d+)(\s|$)", template, wiki_text, 0, re.M)


class IssuesEventHook(BaseGitLabEventHook, BaseIssueEventHook):
    _ISSUE_ACTIONS = {
      "open": ISSUE_ACTION_CREATE,
      "update": ISSUE_ACTION_UPDATE,
      "close": ISSUE_ACTION_CLOSE,
      "reopen": ISSUE_ACTION_REOPEN,
    }

    @property
    def action_type(self):
        _action = self.payload.get('object_attributes', {}).get("action", "")
        return self._ISSUE_ACTIONS.get(_action, None)

    def ignore(self):
        return self.action_type not in [
            ISSUE_ACTION_CREATE,
            ISSUE_ACTION_UPDATE,
            ISSUE_ACTION_CLOSE,
            ISSUE_ACTION_REOPEN,
        ]

    def get_data(self):
        description = self.payload.get('object_attributes', {}).get('description', None)
        project_url = self.payload.get('repository', {}).get('homepage', "")
        user_name = self.payload.get('user', {}).get('username', None)
        state = self.payload.get('object_attributes', {}).get('state', 'opened')

        return {
            "number": self.payload.get('object_attributes', {}).get('iid', None),
            "subject": self.payload.get('object_attributes', {}).get('title', None),
            "url": self.payload.get('object_attributes', {}).get('url', None),
            "user_id": None,
            "user_name": user_name,
            "user_url": os.path.join(os.path.dirname(os.path.dirname(project_url)), user_name),
            "description": self.replace_gitlab_references(project_url, description),
            "status": self.close_status if state == "closed" else self.open_status,
        }


class IssueCommentEventHook(BaseGitLabEventHook, BaseIssueCommentEventHook):
    def ignore(self):
        return self.payload.get('object_attributes', {}).get("noteable_type", None) != "Issue"

    def get_data(self):
        comment_message = self.payload.get('object_attributes', {}).get('note', None)
        project_url = self.payload.get('repository', {}).get('homepage', "")
        issue_url = self.payload.get('issue', {}).get('url', None)
        number = self.payload.get('issue', {}).get('iid', None)
        user_name = self.payload.get('user', {}).get('username', None)
        return {
            "number": number,
            "url": issue_url,
            "user_id": None,
            "user_name": user_name,
            "user_url": os.path.join(os.path.dirname(os.path.dirname(project_url)), user_name),
            "comment_url": self.payload.get('object_attributes', {}).get('url', None),
            "comment_message": self.replace_gitlab_references(project_url, comment_message),
        }


class PushEventHook(BaseGitLabEventHook, BasePushEventHook):
    def get_data(self):
        result = []
        for commit in self.payload.get("commits", []):
            user_name = commit.get('author', {}).get('name', None)
            result.append({
                "user_id": None,
                "user_name": user_name,
                "user_url": None,
                "commit_id": commit.get("id", None),
                "commit_url": commit.get("url", None),
                "commit_message": commit.get("message").strip(),
                "commit_short_message": commit.get("message").split("\n")[0].strip(),
            })
        return result
