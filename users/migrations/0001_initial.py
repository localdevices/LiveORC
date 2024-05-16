# Generated by Django 4.2.3 on 2024-05-16 13:58

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import users.models.user


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('slug', django_extensions.db.fields.ShortUUIDField(blank=True, editable=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='full Name')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email Address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site', verbose_name='Staff Status')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'auth_user',
            },
            managers=[
                ('objects', users.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.group')),
            ],
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of institute', max_length=255, verbose_name='Name')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='institute', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('member', 'Member')], default='member', max_length=32)),
                ('institute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='users.institute')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
