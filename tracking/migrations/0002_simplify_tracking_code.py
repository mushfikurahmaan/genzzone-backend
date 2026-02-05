# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(model_name='trackingcode', name='name'),
        migrations.RemoveField(model_name='trackingcode', name='script_id'),
        migrations.RemoveField(model_name='trackingcode', name='provider'),
        migrations.RemoveField(model_name='trackingcode', name='noscript_content'),
        migrations.RemoveField(model_name='trackingcode', name='placement'),
        migrations.RemoveField(model_name='trackingcode', name='order'),
        migrations.AlterField(
            model_name='trackingcode',
            name='script_content',
            field=models.TextField(
                blank=True,
                help_text='Paste your tracking code (e.g. Meta Pixel). You can include <script> tags; they will be stripped before injection.',
            ),
        ),
        migrations.AlterModelOptions(
            name='trackingcode',
            options={'ordering': ['id'], 'verbose_name': 'Tracking code', 'verbose_name_plural': 'Tracking codes'},
        ),
    ]
