from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_user_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
