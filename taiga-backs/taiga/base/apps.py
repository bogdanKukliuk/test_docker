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

from django.apps import AppConfig


class BaseAppConfig(AppConfig):
    name = "taiga.base"
    verbose_name = "Base App Config"

    def ready(self):
        from .signals.thumbnails import connect_thumbnail_signals
        from .signals.cleanup_files import connect_cleanup_files_signals

        connect_thumbnail_signals()
        connect_cleanup_files_signals()
