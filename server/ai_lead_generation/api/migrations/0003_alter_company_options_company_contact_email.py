# Generated by Django 5.0.1 on 2025-02-24 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_customuser_options_alter_company_table_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name': 'Company', 'verbose_name_plural': 'Companies'},
        ),
        migrations.AddField(
            model_name='company',
            name='contact_email',
            field=models.EmailField(blank=True, help_text='Company contact email', max_length=254, null=True),
        ),
    ]
