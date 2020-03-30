from datetime import datetime

import requests
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, status

from core.models import DMEDPersonInfo


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
        self.token = token or self.obtain_token(username, password)

    @property
    def token(self):
        return cache.get('dmed_token')

    @token.setter
    def token(self, value):
        cache.set('dmed_token', value)
        self.s.headers['Authorization'] = f'Bearer {value}'

    def obtain_token(self, username, password):
        rv = requests.post(url=self.url + self.URL_GET_TOKEN, json=dict(
            systemUsername=self.username,
            systemPassword=self.password
        ))
        return rv.text

    def handle_response(self, rv):
        data = rv.json()
        if isinstance(data, dict) and 'Code' in data:
            raise BadGateway(data.get('Message'))
        return data

    def get_person(self, iin: str):
        """Заполняет пустой или обновляет существующий объект DMEDPersonInfo"""
        rv = self.s.post(self.url + self.URL_GET_PERSONS, json=dict(iin=iin))
        data = self.handle_response(rv)
        if data:
            pi = DMEDPersonInfo()

            r = data[0]
            if r.get('birthDate'):
                r['birthDate'] = datetime.strptime(r['birthDate'], '%Y-%m-%dT%H:%M:%S')

            pi.id = r['id']
            pi.iin = iin
            pi.first_name = r.get('firstName')
            pi.second_name = r.get('secondName')
            pi.last_name = r.get('lastName')
            pi.full_name = r.get('fullName')
            pi.birth_date = r.get('birthDate')
            pi.sex_id = r.get('sexID')
            pi.nationality_id = r.get('nationalityID')
            pi.citizenship_id = r.get('citizenshipID')
            pi.rpn_id = r.get('rpnID')
            pi.master_data_id = r.get('masterDataID')
            return pi

    def get_markers(self, p: DMEDPersonInfo):
        rv = self.s.post(self.url + self.URL_GET_MARKERS, json=dict(personID=p.id, limit=1024))
        return self.handle_response(rv)['data']
