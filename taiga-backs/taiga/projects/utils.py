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


def attach_members(queryset, as_field="members_attr"):
    """Attach a json members representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the members as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(row_to_json(t))
              FROM  (
                        SELECT users_user.id,
                               users_user.username,
                               users_user.full_name,
                               users_user.email,
                               concat(full_name, username) complete_user_name,
                               users_user.color,
                               users_user.photo,
                               users_user.is_active,
                               users_role.id "role",
                               users_role.name role_name
                          FROM projects_membership
                     LEFT JOIN users_user ON projects_membership.user_id = users_user.id
                     LEFT JOIN users_role ON users_role.id = projects_membership.role_id
                         WHERE projects_membership.project_id = {tbl}.id
                      ORDER BY complete_user_name
                    ) t
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_milestones(queryset, as_field="milestones_attr"):
    """Attach a json milestons representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the milestones as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(row_to_json(t))
               FROM (
                        SELECT milestones_milestone.id,
                               milestones_milestone.slug,
                               milestones_milestone.name,
                               milestones_milestone.closed
                          FROM milestones_milestone
                         WHERE milestones_milestone.project_id = {tbl}.id
                      ORDER BY estimated_start
                    ) t
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_closed_milestones(queryset, as_field="closed_milestones_attr"):
    """Attach a closed milestones counter to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the counter as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT COUNT(milestones_milestone.id)
               FROM milestones_milestone
              WHERE milestones_milestone.project_id = {tbl}.id AND
                    milestones_milestone.closed = True
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_notify_policies(queryset, as_field="notify_policies_attr"):
    """Attach a json notification policies representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the notification policies as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(row_to_json(notifications_notifypolicy))
               FROM notifications_notifypolicy
              WHERE notifications_notifypolicy.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_epic_statuses(queryset, as_field="epic_statuses_attr"):
    """Attach a json epic statuses representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the epic statuses as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_epicstatus)
                        ORDER BY projects_epicstatus.order
                    )
               FROM projects_epicstatus
              WHERE projects_epicstatus.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_swimlanes(queryset, as_field="swimlanes_attr"):
    """Attach a json swimlanes representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the swimalne as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_swimlane)
                        ORDER BY projects_swimlane.order
                    )
               FROM projects_swimlane
              WHERE projects_swimlane.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_userstory_statuses(queryset, as_field="userstory_statuses_attr"):
    """Attach a json userstory statuses representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the userstory statuses as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_userstorystatus)
                        ORDER BY projects_userstorystatus.order
                    )
               FROM projects_userstorystatus
              WHERE projects_userstorystatus.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_userstory_duedates(queryset, as_field="userstory_duedates_attr"):
    """Attach a json userstory duedates representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the userstory duedates as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_userstoryduedate)
                        ORDER BY projects_userstoryduedate.order
                    )
               FROM projects_userstoryduedate
              WHERE projects_userstoryduedate.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_points(queryset, as_field="points_attr"):
    """Attach a json points representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the points as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_points)
                        ORDER BY projects_points.order
                    )
               FROM projects_points
              WHERE projects_points.project_id = {tbl}.id
                """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_task_statuses(queryset, as_field="task_statuses_attr"):
    """Attach a json task statuses representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the task statuses as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_taskstatus)
                        ORDER BY projects_taskstatus.order
                    )
               FROM projects_taskstatus
              WHERE projects_taskstatus.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_task_duedates(queryset, as_field="task_duedates_attr"):
    """Attach a json task duedates representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the task duedates as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_taskduedate)
                        ORDER BY projects_taskduedate.order
                    )
               FROM projects_taskduedate
              WHERE projects_taskduedate.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_issue_statuses(queryset, as_field="issue_statuses_attr"):
    """Attach a json issue statuses representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the statuses as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_issuestatus)
                        ORDER BY projects_issuestatus.order
                    )
               FROM projects_issuestatus
              WHERE projects_issuestatus.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_issue_types(queryset, as_field="issue_types_attr"):
    """Attach a json issue types representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the types as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_issuetype)
                        ORDER BY projects_issuetype.order
                    )
               FROM projects_issuetype
              WHERE projects_issuetype.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_issue_duedates(queryset, as_field="issue_duedates_attr"):
    """Attach a json issue duedates representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the duedates as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_issueduedate)
                        ORDER BY projects_issueduedate.order
                    )
               FROM projects_issueduedate
              WHERE projects_issueduedate.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_priorities(queryset, as_field="priorities_attr"):
    """Attach a json priorities representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the priorities as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_priority)
                        ORDER BY projects_priority.order
                    )
               FROM projects_priority
              WHERE projects_priority.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_severities(queryset, as_field="severities_attr"):
    """Attach a json severities representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the severities as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(projects_severity)
                        ORDER BY projects_severity.order
                    )
               FROM projects_severity
              WHERE projects_severity.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_epic_custom_attributes(queryset, as_field="epic_custom_attributes_attr"):
    """Attach a json epic custom attributes representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the epic custom attributes as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(custom_attributes_epiccustomattribute)
                        ORDER BY custom_attributes_epiccustomattribute.order
                    )
               FROM custom_attributes_epiccustomattribute
              WHERE custom_attributes_epiccustomattribute.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_userstory_custom_attributes(queryset, as_field="userstory_custom_attributes_attr"):
    """Attach a json userstory custom attributes representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the userstory custom attributes as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(custom_attributes_userstorycustomattribute)
                        ORDER BY custom_attributes_userstorycustomattribute.order
                    )
               FROM custom_attributes_userstorycustomattribute
              WHERE custom_attributes_userstorycustomattribute.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_task_custom_attributes(queryset, as_field="task_custom_attributes_attr"):
    """Attach a json task custom attributes representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the task custom attributes as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(custom_attributes_taskcustomattribute)
                        ORDER BY custom_attributes_taskcustomattribute.order
                    )
               FROM custom_attributes_taskcustomattribute
              WHERE custom_attributes_taskcustomattribute.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_issue_custom_attributes(queryset, as_field="issue_custom_attributes_attr"):
    """Attach a json issue custom attributes representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the issue custom attributes as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(custom_attributes_issuecustomattribute)
                        ORDER BY custom_attributes_issuecustomattribute.order
                    )
               FROM custom_attributes_issuecustomattribute
              WHERE custom_attributes_issuecustomattribute.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_roles(queryset, as_field="roles_attr"):
    """Attach a json roles representation to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the roles as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    sql = """
             SELECT json_agg(
                        row_to_json(users_role)
                        ORDER BY users_role.order
                    )
               FROM users_role
              WHERE users_role.project_id = {tbl}.id
          """

    sql = sql.format(tbl=model._meta.db_table)
    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_is_fan(queryset, user, as_field="is_fan_attr"):
    """Attach a is fan boolean to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the boolean as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    if user is None or user.is_anonymous:
        sql = "SELECT false"
    else:
        sql = """
                 SELECT COUNT(likes_like.id) > 0
                   FROM likes_like
             INNER JOIN django_content_type ON likes_like.content_type_id = django_content_type.id
                  WHERE django_content_type.model = 'project' AND
                        django_content_type.app_label = 'projects' AND
                        likes_like.user_id = {user_id} AND
                        likes_like.object_id = {tbl}.id
              """

        sql = sql.format(tbl=model._meta.db_table, user_id=user.id)

    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_my_role_permissions(queryset, user, as_field="my_role_permissions_attr"):
    """Attach a permission array to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the permissions as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    if user is None or user.is_anonymous:
        sql = "SELECT '{}'"
    else:
        sql = """
                 SELECT users_role.permissions
                   FROM projects_membership
              LEFT JOIN users_user ON projects_membership.user_id = users_user.id
              LEFT JOIN users_role ON users_role.id = projects_membership.role_id
                  WHERE projects_membership.project_id = {tbl}.id AND
                        users_user.id = {user_id}"""

        sql = sql.format(tbl=model._meta.db_table, user_id=user.id)

    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_private_projects_same_owner(queryset, user, as_field="private_projects_same_owner_attr"):
    """Attach a private projects counter to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the counter as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    if user is None or user.is_anonymous:
        sql = "SELECT 0"
    else:
        sql = """
                 SELECT COUNT(id)
                   FROM projects_project p_aux
                  WHERE p_aux.is_private = True AND
                        p_aux.owner_id = {tbl}.owner_id
              """

        sql = sql.format(tbl=model._meta.db_table, user_id=user.id)

    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_public_projects_same_owner(queryset, user, as_field="public_projects_same_owner_attr"):
    """Attach a public projects counter to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the counter as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    if user is None or user.is_anonymous:
        sql = "SELECT 0"
    else:
        sql = """
                 SELECT COUNT(id)
                   FROM projects_project p_aux
                  WHERE p_aux.is_private = False AND
                        p_aux.owner_id = {tbl}.owner_id
              """

        sql = sql.format(tbl=model._meta.db_table, user_id=user.id)

    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_my_homepage(queryset, user, as_field="my_homepage_attr"):
    """Attach a homepage array to each object of the queryset.

    :param queryset: A Django projects queryset object.
    :param as_field: Attach the settings homepage as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    if user is None or user.is_anonymous:
        sql = "SELECT '{}'"
    else:
        sql = """
                 SELECT homepage
                   FROM settings_userprojectsettings
                  WHERE settings_userprojectsettings.project_id = {tbl}.id AND
                        settings_userprojectsettings.user_id = {user_id}"""

        sql = sql.format(tbl=model._meta.db_table, user_id=user.id)

    queryset = queryset.extra(select={as_field: sql})
    return queryset


def attach_extra_info(queryset, user=None):
    queryset = attach_members(queryset)
    queryset = attach_closed_milestones(queryset)
    queryset = attach_notify_policies(queryset)
    queryset = attach_epic_statuses(queryset)
    queryset = attach_swimlanes(queryset)
    queryset = attach_userstory_statuses(queryset)
    queryset = attach_userstory_duedates(queryset)
    queryset = attach_points(queryset)
    queryset = attach_task_statuses(queryset)
    queryset = attach_task_duedates(queryset)
    queryset = attach_issue_statuses(queryset)
    queryset = attach_issue_duedates(queryset)
    queryset = attach_issue_types(queryset)
    queryset = attach_priorities(queryset)
    queryset = attach_severities(queryset)
    queryset = attach_epic_custom_attributes(queryset)
    queryset = attach_userstory_custom_attributes(queryset)
    queryset = attach_task_custom_attributes(queryset)
    queryset = attach_issue_custom_attributes(queryset)
    queryset = attach_roles(queryset)
    queryset = attach_is_fan(queryset, user)
    queryset = attach_my_role_permissions(queryset, user)
    queryset = attach_private_projects_same_owner(queryset, user)
    queryset = attach_public_projects_same_owner(queryset, user)
    queryset = attach_milestones(queryset)
    queryset = attach_my_homepage(queryset, user)

    return queryset


def attach_basic_info(queryset, user=None):
    """Attach basic information to each object of the queryset. It's a conservative approach,
    could be reduced in future versions.

    :param queryset: A Django projects queryset object.

    :return: Queryset
    """
    queryset = attach_members(queryset)
    queryset = attach_notify_policies(queryset)
    queryset = attach_is_fan(queryset, user)
    queryset = attach_my_role_permissions(queryset, user)
    queryset = attach_private_projects_same_owner(queryset, user)
    queryset = attach_public_projects_same_owner(queryset, user)
    queryset = attach_my_homepage(queryset, user)

    return queryset
