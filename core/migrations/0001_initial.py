# Generated by Django 3.0.4 on 2020-03-30 13:26

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def fill_regions(apps, schema_editor):
    Region = apps.get_model('core', 'Region')
    for r in [
        Region(name='Казахстан'),
        Region(name='АКМОЛИНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-akm.dmed.kz/WebApi2.3/api/'),
        Region(name='АКТЮБИНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-akt.dmed.kz/WebApi2.3/api/'),
        Region(name='АЛМАТИНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-ala.dmed.kz/WebApi2.3/api/'),
        Region(name='АТЫРАУСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-atr.dmed.kz/WebApi2.3/api/'),
        Region(name='ЗАПАДНО-КАЗАХСТАНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-zko.dmed.kz/WebApi2.3/api/'),
        Region(name='ЖАМБЫЛСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-zha.dmed.kz/WebApi2.3/api/'),
        Region(name='КАРАГАНДИНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-krg.dmed.kz/WebApi2.3/api/'),
        Region(name='КОСТАНАЙСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-kos.dmed.kz/WebApi2.3/api/'),
        Region(name='КЫЗЫЛОРДИНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-kzy.dmed.kz/WebApi2.3/api/'),
        Region(name='МАНГИСТАУСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-mng.dmed.kz/WebApi2.3/api/'),
        Region(name='ЮЖНО-КАЗАХСТАНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-uko.dmed.kz/WebApi2.3/api/'),
        Region(name='ПАВЛОДАРСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-pvd.dmed.kz/WebApi2.3/api/'),
        Region(name='СЕВЕРО-КАЗАХСТАНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-sko.dmed.kz/WebApi2.3/api/'),
        Region(name='ВОСТОЧНО-КАЗАХСТАНСКАЯ ОБЛАСТЬ', dmed_url='https://lkp-vko.dmed.kz/WebApi2.3/api/'),
        Region(name='АЛМАТЫ', dmed_url='https://lkp-alm.dmed.kz/WebApi2.3/api/'),
        Region(name='АСТАНА', dmed_url='https://lkp-ast.dmed.kz/WebApi2.3/api/')
    ]:
        r.name = r.name.capitalize()
        r.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkpoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=500)),
                ('location', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DMEDPersonInfo',
            fields=[
                ('add_date', models.DateTimeField(auto_now=True)),
                ('iin', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('id', models.BigIntegerField()),
                ('first_name', models.TextField(blank=True, null=True)),
                ('second_name', models.TextField(blank=True, null=True)),
                ('last_name', models.TextField(blank=True, null=True)),
                ('full_name', models.TextField(blank=True, null=True)),
                ('sex_id', models.IntegerField(blank=True, choices=[(1, 'Male Xix'), (2, 'Female Xix'), (3, 'Male Xx'), (4, 'Female Xx'), (5, 'Male Xxi'), (6, 'Female Xxi')], null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('nationality_id', models.IntegerField(blank=True, null=True)),
                ('citizenship_id', models.IntegerField(blank=True, null=True)),
                ('rpn_id', models.BigIntegerField(blank=True, null=True)),
                ('master_data_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('country', models.CharField(choices=[('KZ', 'Казахстан'), ('RU', 'Россия'), ('CN', 'Китай'), ('UZ', 'Узбекистан'), ('KR', 'Киргизия'), ('TRK', 'Туркменистан')], default='KZ', max_length=10)),
                ('dmed_url', models.TextField(blank=True, null=True)),
                ('dmed_priority', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('contact_number', models.TextField(blank=True, null=True)),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Region')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(max_length=300)),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=10)),
                ('birth_date', models.DateField()),
                ('iin', models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ('first_name', models.TextField(blank=True, max_length=100, null=True)),
                ('second_name', models.TextField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=32, null=True)),
                ('dmed_info', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DMEDPersonInfo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CheckpointPass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('checkpoint', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Checkpoint')),
                ('destination_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enter_checkpoints', to='core.Place')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Person')),
                ('source_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exit_checkpoints', to='core.Place')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Region'),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('region', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Region')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='DMEDPersonMarker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('marker_id', models.IntegerField()),
                ('name', models.CharField(max_length=500)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markers', to='core.DMEDPersonInfo')),
            ],
            options={
                'unique_together': {('marker_id', 'person')},
            },
        ),
        migrations.RunPython(fill_regions)
    ]
