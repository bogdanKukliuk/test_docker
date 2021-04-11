# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_attributes', '0002_issuecustomattributesvalues_taskcustomattributesvalues_userstorycustomattributesvalues'),
    ]

    operations = [
        # Function: Remove a key in a json field
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION "json_object_delete_keys"("json" json, VARIADIC "keys_to_delete" text[])
                               RETURNS json
                              LANGUAGE sql
                             IMMUTABLE
                                STRICT
                                    AS $function$
                       SELECT COALESCE ((SELECT ('{' || string_agg(to_json("key") || ':' || "value", ',') || '}')
                                           FROM json_each("json")
                                          WHERE "key" <> ALL ("keys_to_delete")),
                                        '{}')::json $function$;
            """,
            reverse_sql="""DROP FUNCTION IF EXISTS "json_object_delete_keys"("json" json, VARIADIC "keys_to_delete" text[])
                                           CASCADE;"""
        ),

        # Function: Romeve a key in the json field of *_custom_attributes_values.values
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION "clean_key_in_custom_attributes_values"()
                               RETURNS trigger
                                    AS $clean_key_in_custom_attributes_values$
                               DECLARE
                                       key text;
                                       tablename text;
                                 BEGIN
                                       key := OLD.id::text;
                                       tablename := TG_ARGV[0]::text;

                                     EXECUTE 'UPDATE ' || quote_ident(tablename) || '
                                                 SET attributes_values = json_object_delete_keys(attributes_values, ' ||
                                                                                                 quote_literal(key) || ')';

                                       RETURN NULL;
                                   END; $clean_key_in_custom_attributes_values$
                              LANGUAGE plpgsql;

            """,
            reverse_sql="""DROP FUNCTION IF EXISTS "clean_key_in_custom_attributes_values"()
                                           CASCADE;"""
        ),

        # Trigger: Clean userstorycustomattributes values before remove a userstorycustomattribute
        migrations.RunSQL(
            """
            CREATE TRIGGER "update_userstorycustomvalues_after_remove_userstorycustomattribute"
           AFTER DELETE ON custom_attributes_userstorycustomattribute
              FOR EACH ROW
         EXECUTE PROCEDURE clean_key_in_custom_attributes_values('custom_attributes_userstorycustomattributesvalues');
            """,
            reverse_sql="""DROP TRIGGER IF EXISTS "update_userstorycustomvalues_after_remove_userstorycustomattribute"
                                               ON custom_attributes_userstorycustomattribute
                                          CASCADE;"""
        ),

        # Trigger: Clean taskcustomattributes values before remove a taskcustomattribute
        migrations.RunSQL(
            """
            CREATE TRIGGER "update_taskcustomvalues_after_remove_taskcustomattribute"
           AFTER DELETE ON custom_attributes_taskcustomattribute
              FOR EACH ROW
         EXECUTE PROCEDURE clean_key_in_custom_attributes_values('custom_attributes_taskcustomattributesvalues');
            """,
            reverse_sql="""DROP TRIGGER IF EXISTS "update_taskcustomvalues_after_remove_taskcustomattribute"
                                               ON custom_attributes_taskcustomattribute
                                          CASCADE;"""
        ),

        # Trigger: Clean issuecustomattributes values before remove a issuecustomattribute
        migrations.RunSQL(
            """
            CREATE TRIGGER "update_issuecustomvalues_after_remove_issuecustomattribute"
           AFTER DELETE ON custom_attributes_issuecustomattribute
              FOR EACH ROW
         EXECUTE PROCEDURE clean_key_in_custom_attributes_values('custom_attributes_issuecustomattributesvalues');
            """,
            reverse_sql="""DROP TRIGGER IF EXISTS "update_issuecustomvalues_after_remove_issuecustomattribute"
                                               ON custom_attributes_issuecustomattribute
                                          CASCADE;"""
        )
    ]
