# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db import connection
from taiga.projects.userstories.models import *
from taiga.projects.tasks.models import *
from taiga.projects.issues.models import *
from taiga.projects.models import *

def _fix_tags_model(tags_model):
    table_name = tags_model._meta.db_table
    query = "select id from (select id, unnest(tags) tag from %s) x where tag LIKE '%%,%%'"%(table_name)
    cursor = connection.cursor()
    cursor.execute(query)
    for row in cursor.fetchall():
        id = row[0]
        instance = tags_model.objects.get(id=id)
        instance.tags = [tag.replace(",",  "") for tag in instance.tags]
        instance.save()


def fix_tags(apps, schema_editor):
    _fix_tags_model(UserStory)


class Migration(migrations.Migration):

    dependencies = [
        ('userstories', '0007_userstory_external_reference'),
    ]

    operations = [
        migrations.RunPython(fix_tags),
    ]
