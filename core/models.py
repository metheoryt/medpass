from typing import Optional

from django.db import models
from django.db.models import fields as f, Manager
from django.contrib.auth import models as auth_models
from django.utils import timezone
from .validators import validate_iin


CITIZENSHIP_KZ = 85
CITIZENSHIPS_KZ = 85, 1085


class BaseModel(models.Model):
    class Meta:
        abstract = True
    objects: Manager
    add_date = f.DateTimeField(auto_now=timezone.now)


class Country(BaseModel):
    class Meta:
        ordering = ['-priority', 'name']

    id = f.BigIntegerField(primary_key=True)
    name = f.CharField(max_length=256, default='НЕИЗВЕСТНАЯ СТРАНА')
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
    """Анкета"""

    class Sex(models.TextChoices):
        MALE = 'M'
        FEMALE = 'F'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('doc_id', 'citizenship'), name='unique_doc_id_citizenship')
        ]

    # обязательные
    doc_id = f.CharField('ID документа', max_length=32, help_text='Для Казахстана - ИИН')
    citizenship = models.ForeignKey(Country, verbose_name='Гражданство', on_delete=models.CASCADE,
                                    default=CITIZENSHIP_KZ)

    # опциональные
    full_name = f.CharField('Полное имя', max_length=300, null=True, blank=True)
    sex = f.CharField('Пол', max_length=10, choices=Sex.choices, help_text='M/F - муж/жен', null=True, blank=True)
    birth_date = f.DateField('Дата рождения', null=True, blank=True)

    last_name = f.CharField('Фамилия', max_length=100, null=True, blank=True)
    first_name = f.TextField('Имя', max_length=100, null=True, blank=True)
    second_name = f.TextField('Отчество', max_length=100, null=True, blank=True)
    contact_numbers = f.CharField('Контактные номера телефона', max_length=128, null=True, blank=True)
    residence_place = f.CharField('Место проживания', max_length=512, null=True, blank=True)
    study_place = f.CharField('Место учебы', max_length=512, null=True, blank=True)
    working_place = f.CharField('Место работы', max_length=512, null=True, blank=True)

    had_contact_with_infected = f.BooleanField('Имел контакт с инфицированным', null=True, blank=True)
    been_abroad_last_month = f.BooleanField('Был за рубежом последний месяц', null=True, blank=True)
    extra = f.TextField('Дополнительно', null=True, blank=True)

    # данные DMED
    dmed_id = f.BigIntegerField('ID в DMED', null=True, blank=True)
    dmed_rpn_id = f.BigIntegerField(null=True, blank=True)
    dmed_master_data_id = f.BigIntegerField(null=True, blank=True)
    dmed_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.full_name} / {self.doc_id} {self.citizenship.name}'

    def save(self, *args, **kwargs):
        self.iin = self.iin or None  # против пустых строк
        fio = (self.first_name, self.second_name, self.last_name)
        if not self.full_name and any(fio):
            self.full_name = ' '.join((v for v in fio if v))
        return super(Person, self).save(*args, **kwargs)

    @property
    def iin(self):
        """Для обратной совместимости"""
        return self.doc_id if self.citizenship.id in CITIZENSHIPS_KZ else None

    @iin.setter
    def iin(self, value):
        """Для обратной совместимости"""
        validate_iin(value)
        self.doc_id = value
        self.citizenship = Country.objects.get(pk=CITIZENSHIP_KZ)

    @property
    def temperature(self) -> Optional[float]:
        """Последняя замеренная температура"""
        p = self.passes.order_by('-add_date').last()
        if p:
            return p.temperature


class Marker(BaseModel):
    id = f.IntegerField(primary_key=True)
    name = f.CharField(max_length=512)
    persons = models.ManyToManyField(Person, related_name='markers', blank=True)

    def __str__(self):
        return self.name


class Checkpoint(BaseModel):
    """Контрольно-пропускной пост"""
    name = f.CharField(max_length=500)
    location = f.CharField(max_length=500, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class User(auth_models.AbstractUser):
    """Пользователь проекта - мединспектор"""
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspectors')
    """кпп инспектора"""

    def __str__(self):
        return self.username


class Policeman(BaseModel):
    """Полицейский"""
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, blank=True, related_name='policemans')

    def __str__(self):
        return f'{self.id} @ {self.checkpoint}'


class Vehicle(BaseModel):
    """Транспорт"""
    grnz = f.CharField(primary_key=True, max_length=20)

    def __str__(self):
        return self.grnz


class Camera(BaseModel):
    id = f.UUIDField(primary_key=True)

    # геопозиция
    lon = f.FloatField()
    lat = f.FloatField()
    location = f.CharField(max_length=1000)

    def __str__(self):
        return self.location


class CameraCapture(BaseModel):
    """Захват проезжающего мимо камеры транспорта"""
    id = f.UUIDField(primary_key=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = f.DateTimeField()
    direction = models.CharField(max_length=50)
    raw_data = f.CharField(max_length=50_000)  # сюда сохраним всё тело запроса

    def __str__(self):
        return f"{self.vehicle} @ {self.camera} @ {self.date}"


class CheckpointPass(BaseModel):
    """Акт прохождения КПП"""
    class Direction(models.TextChoices):
        IN = 'in'
        OUT = 'out'

    class Status(models.TextChoices):
        NOT_PASSED = 'not_passed'  # процедура проверки ещё не пройдена
        PASSED = 'passed'  # процедура проверки пройдена

    persons = models.ManyToManyField(Person, through='PersonPassData', related_name='passes')
    inspector = models.ForeignKey(User, verbose_name='Мединспектор', on_delete=models.SET_NULL, null=True)
    checkpoint = models.ForeignKey(Checkpoint, verbose_name='КПП', on_delete=models.SET_NULL, null=True, blank=True)
    source_place = f.CharField('Исходный пункт', max_length=512, null=True, blank=True)
    destination_place = f.CharField('Пункт назначения', max_length=512, null=True, blank=True)
    direction = f.CharField(max_length=10, choices=Direction.choices, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='passes')
    policeman = models.ForeignKey(Policeman, on_delete=models.SET_NULL, null=True, blank=True)
    status = f.CharField('Статус прохождения', max_length=30, choices=Status.choices, default=Status.NOT_PASSED)

    @property
    def person(self):
        # legacy - человек, проходящий КПП
        # FIXME сериализатор DRF не понимает объект, скрытый под property, и не может его сериализовать
        p = self.persons.first()
        if p:
            return p.id

    @property
    def temperature(self):
        # legacy - температура этого человека
        try:
            ppd = PersonPassData.objects.get(person=self.persons.first(), checkpoint_pass=self)
        except PersonPassData.DoesNotExist:
            return
        return ppd.temperature

    def __str__(self):
        return f'{self.persons} @ {self.checkpoint} {self.source_place} -> {self.destination_place}'


class PersonPassData(BaseModel):
    """Данные о прохождении КПП одним человеком"""
    class Meta:
        ordering = ['-add_date']
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    checkpoint_pass = models.ForeignKey(CheckpointPass, on_delete=models.CASCADE)
    temperature = f.FloatField(null=True)  # температура в цельсиях

    def __str__(self):
        return f'{self.person} @ {self.checkpoint_pass} w {self.temperature:.01f} C'
