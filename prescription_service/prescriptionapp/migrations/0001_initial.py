# Generated by Django 4.0 on 2021-12-31 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('national_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
            ],
        ),
    ]