from django.db import models
from django.db.models import fields as f
from django.contrib.auth import models as auth_models
from django.utils import timezone
from .validators import validate_iin


class BaseModel(models.Model):
    class Meta:
        abstract = True

    add_date = f.DateTimeField(auto_now=timezone.now)


class Country(BaseModel):
    class Meta:
        ordering = ['-priority', 'name']

    id = f.BigIntegerField(primary_key=True)
    name = f.CharField(max_length=256)
    priority = f.IntegerField(default=0)

    def __str__(self):
        return self.name


class Region(BaseModel):
    """Регион страны"""
    name = f.TextField()
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    dmed_url = f.TextField(null=True, blank=True)  # для казахстанских регионов
    dmed_priority = f.IntegerField(default=0)  # 0 - самый высокий

    def __str__(self):
        return self.name


class Person(BaseModel):
    """Лицо"""

    class Sex(models.TextChoices):
        MALE = 'M'
        FEMALE = 'F'

    # обязательные
    full_name = f.CharField('полное имя', max_length=300)
    sex = f.CharField('пол', max_length=10, choices=Sex.choices, help_text='M/F - муж/жен')
    birth_date = f.DateField('дата рождения', help_text='YYYY-MM-DD')

    # опциональные
    iin = f.CharField('ИИН', max_length=32, null=True, blank=True, unique=True, validators=[validate_iin])
    last_name = f.CharField('фамилия', max_length=100, null=True, blank=True)
    first_name = f.TextField('имя', max_length=100, null=True, blank=True)
    second_name = f.TextField('отчество', max_length=100, null=True, blank=True)
    contact_numbers = f.CharField('контактные номера телефона', max_length=128, null=True, blank=True, help_text='можно несколько через запятые')
    residence_place = f.CharField('место проживания', max_length=512, null=True, blank=True)
    study_place = f.CharField('место учебы', max_length=512, null=True, blank=True)
    working_place = f.CharField('место работы', max_length=512, null=True, blank=True)
    citizenship = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, help_text='гражданин какой страны?')
    had_contact_with_infected = f.BooleanField('имел контакт с инфицированным', null=True, blank=True)
    been_abroad_last_month = f.BooleanField('был за рубежом последний месяц', null=True, blank=True)
    extra = f.TextField('дополнительно', null=True, blank=True)

    # данные DMED
    dmed_id = f.BigIntegerField('ID в DMED', null=True, blank=True)
    dmed_rpn_id = f.BigIntegerField(null=True, blank=True)
    dmed_master_data_id = f.BigIntegerField(null=True, blank=True)
    dmed_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.full_name} ({self.iin})'

    def save(self, *args, **kwargs):
        self.iin = self.iin or None  # против пустых строк
        fio = (self.first_name, self.second_name, self.last_name)
        if not self.full_name and any(fio):
            self.full_name = ' '.join((v for v in fio if v))
        return super(Person, self).save(*args, **kwargs)


class Marker(BaseModel):
    id = f.IntegerField(primary_key=True)
    name = f.CharField(max_length=512)
    persons = models.ManyToManyField(Person, related_name='markers', blank=True)

    def __str__(self):
        return self.name


# class ForeignVisit(BaseModel):
#     """Записи о пребывании лица в других странах. Если отсутствуют - считаем что лицо не покидало границ Казахстана"""
#     person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='foreign_visits')
#     country = f.CharField('страна', max_length=128)
#     leave_date = f.DateField('дата выезда')


class Checkpoint(BaseModel):
    """Контрольно-пропускной пост"""
    name = f.CharField(max_length=500)
    location = f.CharField(max_length=500, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class User(auth_models.AbstractUser):
    """Пользователь проекта"""
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, blank=True)
    """кпп инспектора"""

    def __str__(self):
        return self.username


class CheckpointPass(BaseModel):
    """Акт прохождения контрольно-пропускного поста"""
    date = f.DateTimeField(auto_now=timezone.now)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    inspector = models.ForeignKey(User, verbose_name='инспектор', on_delete=models.SET_NULL, null=True)
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, blank=True)
    source_place = f.CharField('исходный пункт', max_length=512, null=True, blank=True)
    destination_place = f.CharField('пункт назначения', max_length=512, null=True, blank=True)

    def __str__(self):
        return f'{self.person} @ {self.checkpoint} {self.source_place} -> {self.destination_place}'
