from datetime import datetime

import requests
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, status

from core.models import Person, Marker, Country
import threading
import logging


log = logging.getLogger(__name__)


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
        log.info('requesting new auth token for dmed')
        rv = requests.post(url=self.url + self.URL_GET_TOKEN, json=dict(
            systemUsername=self.username,
            systemPassword=self.password
        ), timeout=4)
        return rv.text

    def handle_response(self, rv):
        data = rv.json()
        log.info(f'dmed rs: {data}')
        if isinstance(data, dict) and 'Code' in data:
            raise BadGateway(f"DMED gateway error - {data.get('Message')!r}")
        elif isinstance(data, dict) and 'message' in data:
            raise BadGateway(f"DMED gateway error - {data.get('message')!r}")
        return data

    def update_person(self, p: Person):
        """Заполняет пустой или обновляет существующий Person"""
        url = self.url + self.URL_GET_PERSONS
        payload = dict(iin=p.doc_id)

        log.info(f'dmed person rq: POST {url}: {payload}')

        rv = self.s.post(url, json=payload, timeout=4)
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
                country, created = Country.objects.get_or_create(pk=r['citizenshipID'])
                p.citizenship = country

            p.dmed_rpn_id = r.get('rpnID')
            p.dmed_master_data_id = r.get('masterDataID')
            return True
        return False

    def update_person_markers(self, p: Person):
        """Добавляет недобавленные маркеры к Person (с автосохранением)"""
        url = self.url + self.URL_GET_MARKERS
        payload = dict(personID=p.dmed_id, limit=1024)
        log.info(f'dmed markers rq: POST {url}: {payload}')
        rv = self.s.post(url, json=payload, timeout=4)
        d = self.handle_response(rv)['data']
        for marker in d:
            p.markers.update_or_create(id=marker['markerID'], defaults={'name': marker['markerName']})
