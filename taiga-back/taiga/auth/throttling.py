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

from taiga.base import throttling


class LoginFailRateThrottle(throttling.GlobalThrottlingMixin, throttling.ThrottleByActionMixin, throttling.SimpleRateThrottle):
    scope = "login-fail"
    throttled_actions = ["create"]

    def throttle_success(self, request, view):
        return True

    def finalize(self, request, response, view):
        if response.status_code == 400:
            self.history.insert(0, self.now)
            self.cache.set(self.key, self.history, self.duration)


class RegisterSuccessRateThrottle(throttling.GlobalThrottlingMixin, throttling.ThrottleByActionMixin, throttling.SimpleRateThrottle):
    scope = "register-success"
    throttled_actions = ["register"]

    def throttle_success(self, request, view):
        return True

    def finalize(self, request, response, view):
        if response.status_code == 201:
            self.history.insert(0, self.now)
            self.cache.set(self.key, self.history, self.duration)

