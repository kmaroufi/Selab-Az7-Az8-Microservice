# Generated by Django 4.0 on 2022-01-07 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usersapp', '0007_remove_admin_id_alter_admin_user_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='name',
        ),
    ]