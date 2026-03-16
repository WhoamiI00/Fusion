from django.db import migrations


def repair_moduleaccess_inventory_management(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'globals_moduleaccess'
            """
        )
        columns = {row[0] for row in cursor.fetchall()}

        if 'inventory_management' in columns:
            return

        if 'database' in columns:
            cursor.execute(
                'ALTER TABLE globals_moduleaccess '
                'RENAME COLUMN database TO inventory_management;'
            )
            return

        cursor.execute(
            'ALTER TABLE globals_moduleaccess '
            'ADD COLUMN inventory_management boolean NOT NULL DEFAULT FALSE;'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('globals', '0006_repair_designation_dept_if_not_basic'),
    ]

    operations = [
        migrations.RunPython(
            repair_moduleaccess_inventory_management,
            migrations.RunPython.noop,
        ),
    ]