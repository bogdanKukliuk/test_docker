# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection
from django.db import models, migrations
from django.contrib.contenttypes.models import ContentType
from taiga.base.utils.contenttypes import update_all_contenttypes

def create_notifications(apps, schema_editor):
    update_all_contenttypes(verbosity=0)
    sql="""
INSERT INTO notifications_watched (object_id, created_date, content_type_id, user_id, project_id)
SELECT task_id AS object_id, now() AS created_date, {content_type_id} AS content_type_id, user_id, project_id
FROM tasks_task_watchers INNER JOIN tasks_task ON tasks_task_watchers.task_id = tasks_task.id""".format(content_type_id=ContentType.objects.get(model='task').id)
    cursor = connection.cursor()
    cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_watched'),
        ('tasks', '0007_auto_20150629_1556'),
    ]

    operations = [
        migrations.RunPython(create_notifications),
        migrations.RemoveField(
            model_name='task',
            name='watchers',
        ),
    ]
