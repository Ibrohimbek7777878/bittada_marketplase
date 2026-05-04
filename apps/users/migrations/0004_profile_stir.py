from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='stir',
            field=models.CharField(blank=True, help_text='STIR (INN) — seller only', max_length=20),
        ),
    ]
