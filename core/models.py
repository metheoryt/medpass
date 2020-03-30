from django.db import models
from django.db.models import fields as f
from django.contrib.auth import models as auth_models
from django.utils import timezone


class BaseModel(models.Model):
    class Meta:
        abstract = True

    add_date = f.DateTimeField(auto_now=timezone.now)


class Countries(models.TextChoices):
    KZ = 'KZ', 'Казахстан'
    RU = 'RU', 'Россия'
    CN = 'CN', 'Китай'
    UZ = 'UZ', 'Узбекистан'
    KR = 'KR', 'Киргизия'
    TRK = 'TRK', 'Туркменистан'


class Region(BaseModel):
    """Регион страны"""
    name = f.TextField()
    country = f.CharField(max_length=10, choices=Countries.choices, default=Countries.KZ)
    dmed_url = f.TextField(null=True, blank=True)  # для казахстанских регионов
    dmed_priority = f.IntegerField(default=0)  # 0 - самый высокий

    def __str__(self):
        return self.name


class Place(BaseModel):
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    address = f.TextField(null=True, blank=True)
    contact_number = f.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.address} ({self.region})'


class DMEDPersonInfo(BaseModel):
    class Sex(models.IntegerChoices):
        MALE_XIX = 1
        FEMALE_XIX = 2
        MALE_XX = 3
        FEMALE_XX = 4
        MALE_XXI = 5
        FEMALE_XXI = 6

    iin = f.CharField(max_length=32, primary_key=True)
    id = f.BigIntegerField()

    first_name = f.TextField(null=True, blank=True)
    second_name = f.TextField(null=True, blank=True)
    last_name = f.TextField(null=True, blank=True)
    full_name = f.TextField(null=True, blank=True)
    sex_id = f.IntegerField(choices=Sex.choices, null=True, blank=True)
    birth_date = f.DateField(null=True, blank=True)
    nationality_id = f.IntegerField(null=True, blank=True)
    citizenship_id = f.IntegerField(null=True, blank=True)
    rpn_id = f.BigIntegerField(null=True, blank=True)
    master_data_id = f.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.id} ({self.iin})'


class DMEDPersonMarker(BaseModel):
    class Meta:
        unique_together = (('marker_id', 'person'),)

    marker_id = f.IntegerField()
    name = f.CharField(max_length=500)
    person = models.ForeignKey(DMEDPersonInfo, on_delete=models.CASCADE, related_name='markers')

    def __str__(self):
        return f'<{self.person}> {self.marker_id} {self.name}'


class Person(BaseModel):
    """Лицо"""

    class Sex(models.TextChoices):
        MALE = 'M'
        FEMALE = 'F'

    # обязательные
    full_name = f.CharField('полное имя', max_length=300)
    sex = f.CharField('пол', max_length=10, choices=Sex.choices, help_text='M/F - муж/жен')
    birth_date = f.DateField('дата рождения', help_text='YYY-MM-DD')

    # опциональные
    iin = f.CharField('ИИН', max_length=32, null=True, blank=True, unique=True)
    last_name = f.CharField('фамилия', max_length=100, null=True, blank=True)
    first_name = f.TextField('имя', max_length=100, null=True, blank=True)
    second_name = f.TextField('отчество', max_length=100, null=True, blank=True)
    contact_numbers = f.CharField('контактные номера телефона', max_length=128, null=True, blank=True, help_text='можно несколько через запятые')
    residence_place = models.ForeignKey(Place, verbose_name='место проживания', related_name='residents', on_delete=models.SET_NULL, null=True, blank=True)
    study_place = models.ForeignKey(Place, verbose_name='место учебы', related_name='students', on_delete=models.SET_NULL, null=True, blank=True)
    citizenship = f.CharField('гражданство', max_length=256, null=True, blank=True, help_text='гражданин какой страны?')
    had_contact_with_infected = f.BooleanField('имел контакт с инфицированным', null=True, blank=True)
    been_abroad_last_month = f.BooleanField('был за рубежом последний месяц', null=True, blank=True)
    extra = f.TextField('дополнительно', null=True, blank=True)

    # данные конкретной системы
    dmed_info = models.OneToOneField(DMEDPersonInfo, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.full_name} ({self.iin})'

    def save(self, *args, **kwargs):
        self.iin = self.iin or None
        fio = (self.first_name, self.second_name, self.last_name)
        if not self.full_name and any(fio):
            self.full_name = ' '.join((v for v in fio if v))
        return super(Person, self).save(*args, **kwargs)

    def dmed_update(self, r: DMEDPersonInfo):
        if r.iin:
            self.iin = r.iin
        if r.full_name:
            self.full_name = r.full_name
        if r.first_name:
            self.first_name = r.first_name
        if r.second_name:
            self.second_name = r.second_name
        if r.last_name:
            self.last_name = r.last_name
        if r.sex_id:
            self.sex = self.Sex.FEMALE if r.sex_id in [r.Sex.FEMALE_XIX, r.Sex.FEMALE_XX, r.Sex.FEMALE_XXI] else self.Sex.MALE
        if r.birth_date:
            self.birth_date = r.birth_date
        self.dmed_info = r


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
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True)
    """кпп инспектора"""

    def __str__(self):
        return self.username


class CheckpointPass(BaseModel):
    """Акт прохождения контрольно-пропускного поста"""
    date = f.DateTimeField(auto_now=timezone.now)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    inspector = models.ForeignKey(User, verbose_name='инспектор', on_delete=models.SET_NULL, null=True)
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, blank=True)
    source_place = models.ForeignKey(Place, related_name='exit_checkpoints', on_delete=models.SET_NULL, null=True, blank=True)
    destination_place = models.ForeignKey(Place, related_name='enter_checkpoints', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.person} @ {self.checkpoint} {self.source_place} -> {self.destination_place}'
