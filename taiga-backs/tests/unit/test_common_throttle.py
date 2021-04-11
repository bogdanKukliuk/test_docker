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

from django.test import RequestFactory
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser

from taiga.base.throttling import CommonThrottle
from taiga.users.models import User


def test_user_no_write_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-write'] = None
    request = rf.post("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    for x in range(100):
        assert throttling.allow_request(request, None)
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-write'] = None

def test_user_simple_write_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-write'] = "1/min"
    request = rf.post("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-write'] = None

def test_user_multi_write_first_small_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-write'] = ["1/min", "10/min"]
    request = rf.post("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-write'] = None

def test_user_multi_write_first_big_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-write'] = ["10/min", "1/min"]
    request = rf.post("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-write'] = None

def test_user_no_read_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None
    request = rf.get("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    for x in range(100):
        assert throttling.allow_request(request, None)
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None

def test_user_simple_read_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = "1/min"
    request = rf.get("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None

def test_user_multi_read_first_small_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = ["1/min", "10/min"]
    request = rf.get("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None

def test_user_multi_read_first_big_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = ["10/min", "1/min"]
    request = rf.get("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None

def test_whitelisted_user_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = "1/min"
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = [1]
    request = rf.get("/test")
    request.user = User(id=1)
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None)
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = []

def test_not_whitelisted_user_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = "1/min"
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = [1]
    request = rf.get("/test")
    request.user = User(id=2)
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user-read'] = None
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = []

def test_anon_no_write_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-write'] = None
    request = rf.post("/test")
    request.user = AnonymousUser()
    throttling = CommonThrottle()
    for x in range(100):
        assert throttling.allow_request(request, None)
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-write'] = None

def test_anon_simple_write_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-write'] = "1/min"
    request = rf.post("/test")
    request.user = AnonymousUser()
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-write'] = None

def test_anon_multi_write_first_small_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-write'] = ["1/min", "10/min"]
    request = rf.post("/test")
    request.user = AnonymousUser()
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-write'] = None

def test_anon_multi_write_first_big_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-write'] = ["10/min", "1/min"]
    request = rf.post("/test")
    request.user = AnonymousUser()
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-write'] = None

def test_anon_no_read_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None
    request = rf.get("/test")
    request.user = AnonymousUser()
    throttling = CommonThrottle()
    for x in range(100):
        assert throttling.allow_request(request, None)
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None

def test_anon_simple_read_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = "1/min"
    request = rf.get("/test")
    request.user = AnonymousUser()
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None

def test_anon_multi_read_first_small_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = ["1/min", "10/min"]
    request = rf.get("/test")
    request.user = AnonymousUser()
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None

def test_anon_multi_read_first_big_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = ["10/min", "1/min"]
    request = rf.get("/test")
    request.user = AnonymousUser()
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None

def test_whitelisted_anon_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = "1/min"
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = ["127.0.0.1"]
    request = rf.get("/test")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "127.0.0.1"
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None)
    for x in range(100):
        assert throttling.allow_request(request, None)
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = []

def test_not_whitelisted_anon_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = "1/min"
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = ["127.0.0.1"]
    request = rf.get("/test")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "127.0.0.2"
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = []

def test_whitelisted_subnet_anon_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = "1/min"
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = ["192.168.0.0/24"]
    request = rf.get("/test")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "192.168.0.123"
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None)
    for x in range(100):
        assert throttling.allow_request(request, None)
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = []

def test_not_whitelisted_subnet_anon_throttling(settings, rf):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = "1/min"
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = ["192.168.0.0/24"]
    request = rf.get("/test")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "192.168.1.123"
    throttling = CommonThrottle()
    assert throttling.allow_request(request, None)
    assert throttling.allow_request(request, None) is False
    for x in range(100):
        assert throttling.allow_request(request, None) is False
    cache.clear()
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon-read'] = None
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_WHITELIST'] = []
