# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0004_auto_20150114_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='priority',
            field=models.ForeignKey(blank=True, null=True, to='projects.Priority', related_name='issues', verbose_name='priority', on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='severity',
            field=models.ForeignKey(blank=True, null=True, to='projects.Severity', related_name='issues', verbose_name='severity', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.ForeignKey(blank=True, null=True, to='projects.IssueStatus', related_name='issues', verbose_name='status', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='type',
            field=models.ForeignKey(blank=True, null=True, to='projects.IssueType', related_name='issues', verbose_name='type', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
