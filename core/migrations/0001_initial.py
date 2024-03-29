# Generated by Django 3.0.5 on 2020-04-22 14:34

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
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
            name='Camera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('location', models.CharField(max_length=1000, unique=True)),
                ('lon', models.FloatField(null=True)),
                ('lat', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Checkpoint',
            fields=[
                ('add_date', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=500)),
                ('location', models.CharField(blank=True, max_length=500, null=True)),
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
                ('source_place', models.CharField(blank=True, max_length=512, null=True, verbose_name='Исходный пункт')),
                ('destination_place', models.CharField(blank=True, max_length=512, null=True, verbose_name='Пункт назначения')),
                ('status', models.CharField(choices=[('not_passed', 'Not Passed'), ('passed', 'Passed')], default='not_passed', max_length=30, verbose_name='Статус прохождения')),
                ('checkpoint', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Checkpoint', verbose_name='КПП')),
                ('inspector', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Мединспектор')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('add_date', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='НЕИЗВЕСТНАЯ СТРАНА', max_length=256)),
                ('priority', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-priority', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('doc_id', models.CharField(help_text='Для Казахстана - ИИН', max_length=32, verbose_name='ID документа')),
                ('full_name', models.CharField(blank=True, max_length=300, null=True, verbose_name='Полное имя')),
                ('sex', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], help_text='M/F - муж/жен', max_length=10, null=True, verbose_name='Пол')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Фамилия')),
                ('first_name', models.TextField(blank=True, max_length=100, null=True, verbose_name='Имя')),
                ('second_name', models.TextField(blank=True, max_length=100, null=True, verbose_name='Отчество')),
                ('contact_numbers', models.CharField(blank=True, max_length=128, null=True, verbose_name='Контактные номера телефона')),
                ('residence_place', models.CharField(blank=True, max_length=512, null=True, verbose_name='Место проживания')),
                ('study_place', models.CharField(blank=True, max_length=512, null=True, verbose_name='Место учебы')),
                ('working_place', models.CharField(blank=True, max_length=512, null=True, verbose_name='Место работы')),
                ('had_contact_with_infected', models.BooleanField(blank=True, null=True, verbose_name='Имел контакт с инфицированным')),
                ('been_abroad_last_month', models.BooleanField(blank=True, null=True, verbose_name='Был за рубежом последний месяц')),
                ('extra', models.TextField(blank=True, null=True, verbose_name='Дополнительно')),
                ('dmed_id', models.BigIntegerField(blank=True, null=True, verbose_name='ID в DMED')),
                ('dmed_rpn_id', models.BigIntegerField(blank=True, null=True)),
                ('dmed_master_data_id', models.BigIntegerField(blank=True, null=True)),
                ('citizenship', models.ForeignKey(default=85, on_delete=django.db.models.deletion.CASCADE, to='core.Country', verbose_name='Гражданство')),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('add_date', models.DateTimeField(auto_now=True)),
                ('grnz', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('model', models.CharField(blank=True, max_length=200, null=True)),
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
                ('dmed_url', models.TextField(blank=True, null=True)),
                ('dmed_priority', models.IntegerField(default=0)),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonPassData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now=True)),
                ('temperature', models.FloatField(null=True)),
                ('checkpoint_pass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.CheckpointPass')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Person')),
            ],
            options={
                'ordering': ['-add_date'],
            },
        ),
        migrations.AddField(
            model_name='person',
            name='dmed_region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Region'),
        ),
        migrations.CreateModel(
            name='Marker',
            fields=[
                ('add_date', models.DateTimeField(auto_now=True)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('persons', models.ManyToManyField(blank=True, related_name='markers', to='core.Person')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='checkpointpass',
            name='persons',
            field=models.ManyToManyField(blank=True, related_name='passes', through='core.PersonPassData', to='core.Person'),
        ),
        migrations.AddField(
            model_name='checkpointpass',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='passes', to='core.Vehicle'),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Region'),
        ),
        migrations.CreateModel(
            name='CameraCapture',
            fields=[
                ('add_date', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('raw_data', models.CharField(max_length=50000)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Camera')),
                ('checkpoint_pass', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='camera_capture', to='core.CheckpointPass')),
                ('persons', models.ManyToManyField(blank=True, related_name='captures', to='core.Person')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Vehicle')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='camera',
            name='checkpoint',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cameras', to='core.Checkpoint'),
        ),
        migrations.AddField(
            model_name='user',
            name='checkpoint',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspectors', to='core.Checkpoint'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AddConstraint(
            model_name='personpassdata',
            constraint=models.UniqueConstraint(fields=('person', 'checkpoint_pass'), name='checkpointpass_person_unique'),
        ),
        migrations.AddConstraint(
            model_name='person',
            constraint=models.UniqueConstraint(fields=('doc_id', 'citizenship'), name='unique_doc_id_citizenship'),
        ),
    ]
