# Generated for teaching_languages field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camps', '0002_add_discount_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='surfcamp',
            name='teaching_languages',
            field=models.JSONField(blank=True, default=list, verbose_name='Языки обучения'),
        ),
    ]
