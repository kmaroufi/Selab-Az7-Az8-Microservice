# Generated by Django 4.0 on 2021-12-29 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewPatientEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('national_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
            ],
        ),
    ]