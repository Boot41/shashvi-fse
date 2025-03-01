# Generated by Django 5.0.2 on 2025-02-24 15:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_lead_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='about',
            field=models.TextField(blank=True, help_text='Description of the company'),
        ),
        migrations.CreateModel(
            name='Outreach',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_content', models.TextField()),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outreach_emails', to='api.company')),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
    ]
