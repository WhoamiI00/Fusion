from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('globals', '0005_moduleaccess_patent_management'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE globals_designation '
                'ADD COLUMN IF NOT EXISTS dept_if_not_basic_id integer NULL;'
            ),
            reverse_sql=(
                'ALTER TABLE globals_designation '
                'DROP COLUMN IF EXISTS dept_if_not_basic_id;'
            ),
        ),
    ]