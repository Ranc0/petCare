# Generated by Django 4.2.5 on 2025-03-17 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_pet_birth_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='birth_date',
            field=models.DateField(null=True),
        ),
    ]
