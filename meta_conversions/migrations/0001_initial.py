# Placeholder migration - meta_conversions has no models, only services.
# Also drops orphaned tracking_trackingcode table if it exists (tracking app removed).
from django.db import migrations


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS tracking_trackingcode;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
