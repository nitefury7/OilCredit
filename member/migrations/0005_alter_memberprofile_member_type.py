# Generated by Django 4.0.4 on 2022-05-10 03:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0004_remove_invoice_credit_memberprofile_credit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberprofile',
            name='member_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='member.membertype'),
        ),
    ]
