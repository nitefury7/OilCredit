# Generated by Django 4.0.4 on 2022-05-13 07:25

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=2000)),
                ('rate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='MemberType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=1000)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='MemberProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.SmallIntegerField(choices=[(0, 'Male'), (1, 'Female'), (2, 'Other')])),
                ('city', models.CharField(blank=True, max_length=20)),
                ('state', models.CharField(blank=True, max_length=20)),
                ('zip_code', models.BigIntegerField(blank=True, null=True)),
                ('contact', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('credit', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('member_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='member.membertype')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('order_timestamp', models.DateTimeField()),
                ('action_timestamp', models.DateTimeField(blank=True, null=True)),
                ('status', models.SmallIntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Rejected')], default=0)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.employeeprofile')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member.item')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member.memberprofile')),
            ],
        ),
    ]
