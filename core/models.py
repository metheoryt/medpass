from typing import Optional

from django.conf import settings
from django.db import models
from django.db.models import fields as f, Manager, constraints
from django.contrib.auth import models as auth_models
from django.utils import timezone


from .validators import validate_iin
import logging

log = logging.getLogger(__name__)


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
        m = f'#{self.doc_id}'
        if self.full_name:
            m += f' / {self.full_name}'
        return m

    def save(self, *args, **kwargs):
        self.iin = self.iin or None  # против пустых строк
        fio = (self.first_name, self.second_name, self.last_name)
        if not self.full_name and any(fio):
            self.full_name = ' '.join((v for v in fio if v))
        return super(Person, self).save(*args, **kwargs)

    @property
    def iin(self):
        """Для обратной совместимости"""
        if self.citizenship.id in CITIZENSHIPS_KZ:
            return self.doc_id

    @iin.setter
    def iin(self, value):
        """Для обратной совместимости"""
        if value:
            validate_iin(value)
            self.doc_id = value
            self.citizenship = Country.objects.get(pk=CITIZENSHIP_KZ)

    @property
    def temperature(self) -> Optional[float]:
        """Последняя замеренная температура"""
        p = self.passes.order_by('-add_date').last()
        if p:
            return p.temperature

    def update_from_dmed(self):
        for region in Region.objects.filter(dmed_url__isnull=False).order_by('dmed_priority'):
            try:
                updated = self.update_from_dmed_region(region)
            except Exception as e:
                log.warning(f'error while fetching {region.dmed_url}: {e}')
            else:
                if updated:
                    log.info(f'updated from {region.dmed_url}')
                    return True
            return False

    def update_from_dmed_region(self, region):
        from .service import DMEDService
        dmed = DMEDService(url=region.dmed_url, username=settings.DMED_LOGIN, password=settings.DMED_PASSWORD)
        updated = dmed.update_person(self)
        if updated:
            # если апдейт успешен, сохраняем анкету
            self.dmed_region = region  # запомним откуда получили информацию
            self.save()
            updated = dmed.update_person_detail(self)
            if updated:
                self.save()
            dmed.update_person_markers(self)
        return updated


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


class Vehicle(BaseModel):
    """Транспорт"""
    grnz = f.CharField(primary_key=True, max_length=20)
    model = f.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'{self.grnz} {self.model or "unknown model"}'


class Camera(BaseModel):
    id = f.UUIDField(primary_key=True)

    # геопозиция
    lon = f.FloatField()
    lat = f.FloatField()
    location = f.CharField(max_length=1000)
    # с каким КПП связана
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, null=True, blank=True, related_name='cameras')

    def __str__(self):
        return self.location


class CheckpointPass(BaseModel):
    """Акт прохождения КПП"""
    class Direction(models.TextChoices):
        IN = 'in'
        OUT = 'out'

    class Status(models.TextChoices):
        NOT_PASSED = 'not_passed'  # процедура проверки ещё не пройдена
        PASSED = 'passed'  # процедура проверки пройдена

    persons = models.ManyToManyField(Person, through='PersonPassData', related_name='passes', blank=True)
    inspector = models.ForeignKey(User, verbose_name='Мединспектор', on_delete=models.SET_NULL, null=True)
    checkpoint = models.ForeignKey(Checkpoint, verbose_name='КПП', on_delete=models.SET_NULL, null=True, blank=True)
    source_place = f.CharField('Исходный пункт', max_length=512, null=True, blank=True)
    destination_place = f.CharField('Пункт назначения', max_length=512, null=True, blank=True)
    direction = f.CharField(max_length=10, choices=Direction.choices, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='passes')
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
        m = ''
        if self.source_place:
            m += f'{self.source_place} -> '
        m += f'{self.checkpoint}'
        if self.destination_place:
            m += f' -> {self.destination_place}'
        if self.vehicle:
            m += f' @{self.vehicle}'
        return m


class CameraCapture(BaseModel):
    """Захват проезжающего мимо камеры транспорта"""
    id = f.UUIDField(primary_key=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    persons = models.ManyToManyField(Person, related_name='captures')
    date = f.DateTimeField()
    raw_data = f.CharField(max_length=50_000)  # сюда сохраним всё тело запроса
    checkpoint_pass = models.OneToOneField(
        CheckpointPass, on_delete=models.SET_NULL, null=True, blank=True, related_name='camera_capture'
    )

    def create_or_update_checkpoint_pass(self, inspector):
        if not self.checkpoint_pass:
            checkpoint_pass = CheckpointPass()
            self.checkpoint_pass = checkpoint_pass
            log.info(f'{checkpoint_pass} created')
        else:
            checkpoint_pass = self.checkpoint_pass
        checkpoint_pass.vehicle = self.vehicle
        checkpoint_pass.checkpoint = inspector.checkpoint
        checkpoint_pass.inspector = inspector
        checkpoint_pass.save()
        self.save()
        for person in self.persons.all():
            checkpoint_pass.persons.add(person)

        return checkpoint_pass

    def __str__(self):
        return f"{self.vehicle} @ {self.camera} @ {self.date.strftime('%Y-%m-%d %H:%M:%S')}"


class PersonPassData(BaseModel):
    """Данные о прохождении КПП одним человеком"""
    class Meta:
        ordering = ['-add_date']
        constraints = [
            constraints.UniqueConstraint(fields=('person', 'checkpoint_pass'), name='checkpointpass_person_unique')
        ]
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    checkpoint_pass = models.ForeignKey(CheckpointPass, on_delete=models.CASCADE)
    temperature = f.FloatField(null=True)  # температура в цельсиях

    def __str__(self):
        m = f'{self.person}'
        if self.temperature:
            m += f' {self.temperature:.01f} °C'
        m += f' ({self.checkpoint_pass})'
        return m
