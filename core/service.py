from datetime import datetime

import requests
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, status

from core.models import Person, Marker, Country


class BadGateway(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = _('Bad gateway.')
    default_code = 'bad_gateway'


class DMEDService:
    URL_GET_TOKEN = 'Authentication/SignInExternalApp'
    URL_GET_PERSONS = 'Person/GetPersons'
    URL_GET_MARKERS = 'Person/GetPersonMarkers'

    def __init__(self, url, token=None, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        self.s = requests.Session()
        if token:
            self.token = token
        elif not self.token:
            self.token = self.obtain_token()
        self.s.headers['Authorization'] = f'Bearer {self.token}'

    @property
    def token(self):
        return cache.get('dmed_token')

    @token.setter
    def token(self, value):
        cache.set('dmed_token', value, 60 * 60)

    def obtain_token(self):
        rv = requests.post(url=self.url + self.URL_GET_TOKEN, json=dict(
            systemUsername=self.username,
            systemPassword=self.password
        ))
        return rv.text

    def handle_response(self, rv):
        data = rv.json()
        if isinstance(data, dict) and 'Code' in data:
            raise BadGateway(f"DMED gateway error - {data.get('Message')!r}")
        elif isinstance(data, dict) and 'message' in data:
            raise BadGateway(f"DMED gateway error - {data.get('message')!r}")
        return data

    def update_person(self, p: Person):
        """Заполняет пустой или обновляет существующий Person"""
        rv = self.s.post(self.url + self.URL_GET_PERSONS, json=dict(iin=p.iin))
        data = self.handle_response(rv)
        if data:
            r = data[0]
            if r.get('birthDate'):
                r['birthDate'] = datetime.strptime(r['birthDate'], '%Y-%m-%dT%H:%M:%S')

            p.dmed_id = r['id']
            p.first_name = r.get('firstName') or p.first_name
            p.second_name = r.get('secondName') or p.second_name
            p.last_name = r.get('lastName') or p.last_name
            p.full_name = r.get('fullName') or p.full_name
            p.birth_date = r.get('birthDate') or p.birth_date
            sex_id = r.get('sexID')
            if sex_id:
                p.sex = p.Sex.FEMALE if sex_id in [2, 4, 6] else p.Sex.MALE
            # p.nationality = r.get('nationalityID')

            if r.get('citizenshipID') is not None:
                try:
                    p.citizenship = Country.objects.get(pk=r['citizenshipID'])
                except Country.DoesNotExist:
                    pass

            p.dmed_rpn_id = r.get('rpnID')
            p.dmed_master_data_id = r.get('masterDataID')
            return p

    def update_person_markers(self, p: Person):
        """Добавляет недобавленные маркеры к Person (с автосохранением)"""
        rv = self.s.post(self.url + self.URL_GET_MARKERS, json=dict(personID=p.dmed_id, limit=1024))
        d = self.handle_response(rv)['data']
        for marker in d:
            try:
                m = Marker.objects.get(id=marker['markerID'])
            except Marker.DoesNotExist:
                p.markers.create(id=marker['markerID'], name=marker['markerName'])
            else:
                if not p.markers.exists(id=marker['markerID']):
                    p.markers.add(m)
