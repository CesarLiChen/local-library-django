# Generated by Django 4.2.3 on 2023-07-22 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_rename_data_of_death_author_date_of_death'),
    ]

    operations = [
        migrations.CreateModel(
            name='Secret',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Dummy field, no use for this app', max_length=200)),
            ],
        ),
    ]
