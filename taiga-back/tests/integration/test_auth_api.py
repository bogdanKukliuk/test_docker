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
from django.core import mail

from .. import factories

pytestmark = pytest.mark.django_db


@pytest.fixture
def register_form():
    return {"username": "username",
            "password": "password",
            "full_name": "fname",
            "email": "user@email.com",
            "accepted_terms": True,
            "type": "public"}


def test_respond_201_when_public_registration_is_enabled(client, settings, register_form):
    settings.PUBLIC_REGISTER_ENABLED = True
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 201


def test_respond_400_when_public_registration_is_disabled(client, register_form, settings):
    settings.PUBLIC_REGISTER_ENABLED = False
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 400


def test_respond_400_when_the_email_domain_isnt_in_allowed_domains(client, register_form, settings):
    settings.PUBLIC_REGISTER_ENABLED = True
    settings.USER_EMAIL_ALLOWED_DOMAINS = ['other-domain.com']
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 400


def test_respond_201_when_the_email_domain_is_in_allowed_domains(client, settings, register_form):
    settings.PUBLIC_REGISTER_ENABLED = True
    settings.USER_EMAIL_ALLOWED_DOMAINS = ['email.com']
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 201


def test_respond_201_with_invitation_login(client, settings):
    settings.PUBLIC_REGISTER_ENABLED = False
    user = factories.UserFactory()
    membership = factories.MembershipFactory(user=user)

    auth_data = {
        "type": "normal",
        "invitation_token": membership.token,
        "username": user.username,
        "password": user.username,
    }

    response = client.post(reverse("auth-list"), auth_data)

    assert response.status_code == 200, response.data


def test_response_200_in_public_registration(client, settings):
    settings.PUBLIC_REGISTER_ENABLED = True
    form = {
        "type": "public",
        "username": "mmcfly",
        "full_name": "martin seamus mcfly",
        "email": "mmcfly@bttf.com",
        "password": "password",
        "accepted_terms": True,
    }

    response = client.post(reverse("auth-register"), form)
    assert response.status_code == 201
    assert response.data["username"] == "mmcfly"
    assert response.data["email"] == "mmcfly@bttf.com"
    assert response.data["full_name"] == "martin seamus mcfly"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "You've been Taigatized!"


def test_respond_400_if_username_is_invalid(client, settings, register_form):
    settings.PUBLIC_REGISTER_ENABLED = True

    register_form.update({"username": "User Examp:/e"})
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 400

    register_form.update({"username": 300*"a"})
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 400


def test_respond_400_if_username_or_email_is_duplicate(client, settings, register_form):
    settings.PUBLIC_REGISTER_ENABLED = True

    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 201

    register_form["username"] = "username"
    register_form["email"] = "ff@dd.com"
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 400


def test_auth_uppercase_ignore(client, settings):
    settings.PUBLIC_REGISTER_ENABLED = True

    register_form = {"username": "Username",
                     "password": "password",
                     "full_name": "fname",
                     "email": "User@email.com",
                     "accepted_terms": True,
                     "type": "public"}
    response = client.post(reverse("auth-register"), register_form)

    #Only exists one user with the same lowercase version of username/password
    login_form = {"type": "normal",
                  "username": "Username",
                  "password": "password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 200

    login_form = {"type": "normal",
                  "username": "User@email.com",
                  "password": "password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 200

    #Now we have two users with the same lowercase version of username/password
    # 1.- The capitalized version works
    register_form = {"username": "username",
                     "password": "password",
                     "full_name": "fname",
                     "email": "user@email.com",
                     "accepted_terms": True,
                     "type": "public"}
    response = client.post(reverse("auth-register"), register_form)

    login_form = {"type": "normal",
                  "username": "Username",
                  "password": "password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 200

    login_form = {"type": "normal",
                  "username": "User@email.com",
                  "password": "password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 200

    # 2.- If we capitalize a new version it doesn't
    login_form = {"type": "normal",
                  "username": "uSername",
                  "password": "password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 400

    login_form = {"type": "normal",
                  "username": "uSer@email.com",
                  "password": "password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 400


def test_login_fail_throttling(client, settings):
    settings.PUBLIC_REGISTER_ENABLED = True
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login-fail"] = "1/minute"

    register_form = {"username": "valid_username_login_fail",
                     "password": "valid_password",
                     "full_name": "fullname",
                     "email": "valid_username_login_fail@email.com",
                     "accepted_terms": True,
                     "type": "public"}
    response = client.post(reverse("auth-register"), register_form)

    login_form = {"type": "normal",
                  "username": "valid_username_login_fail",
                  "password": "valid_password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 200

    login_form = {"type": "normal",
                  "username": "invalid_username_login_fail",
                  "password": "invalid_password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 400

    login_form = {"type": "normal",
                  "username": "invalid_username_login_fail",
                  "password": "invalid_password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 429

    login_form = {"type": "normal",
                  "username": "valid_username_login_fail",
                  "password": "valid_password"}

    response = client.post(reverse("auth-list"), login_form)
    assert response.status_code == 429

    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login-fail"] = None

def test_register_success_throttling(client, settings):
    settings.PUBLIC_REGISTER_ENABLED = True
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["register-success"] = "1/minute"

    register_form = {"username": "valid_username_register_success",
                     "password": "valid_password",
                     "full_name": "fullname",
                     "email": "",
                     "accepted_terms": True,
                     "type": "public"}
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 400

    register_form = {"username": "valid_username_register_success",
                     "password": "valid_password",
                     "full_name": "fullname",
                     "email": "valid_username_register_success@email.com",
                     "accepted_terms": True,
                     "type": "public"}
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 201

    register_form = {"username": "valid_username_register_success2",
                     "password": "valid_password2",
                     "full_name": "fullname",
                     "email": "valid_username_register_success2@email.com",
                     "accepted_terms": True,
                     "type": "public"}
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 429

    register_form = {"username": "valid_username_register_success2",
                     "password": "valid_password2",
                     "full_name": "fullname",
                     "email": "",
                     "accepted_terms": True,
                     "type": "public"}
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 429

    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["register-success"] = None


INVALID_NAMES = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod",
    "an <script>evil()</script> example",
    "http://testdomain.com",
    "https://testdomain.com",
    "Visit http://testdomain.com",
]

@pytest.mark.parametrize("full_name", INVALID_NAMES)
def test_register_sanitize_invalid_user_full_name(client, settings, full_name, register_form):
    settings.PUBLIC_REGISTER_ENABLED = True
    register_form["full_name"] = full_name
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 400

VALID_NAMES = [
    "martin seamus mcfly"
]

@pytest.mark.parametrize("full_name", VALID_NAMES)
def test_register_sanitize_valid_user_full_name(client, settings, full_name, register_form):
    settings.PUBLIC_REGISTER_ENABLED = True
    register_form["full_name"] = full_name
    response = client.post(reverse("auth-register"), register_form)
    assert response.status_code == 201




