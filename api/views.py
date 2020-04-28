import logging
from collections import defaultdict
from datetime import datetime

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.utils import json
from rest_framework.views import APIView

from api2.consumers import CameraConsumer
from core.models import Camera, CameraCapture, Vehicle, Person, CITIZENSHIPS_KZ, CITIZENSHIP_KZ, Country, Checkpoint

log = logging.getLogger(__name__)


def fetch_camera_checkpoint(camera_name):
    log.debug('requesting egsv for checkpoints')
    r = requests.get(
        'https://application-rubezh.egsv.kz/checkpoints?sources=1', timeout=5
    ).json()['checkpoints']
    log.debug(f'egsv response: {r}')

    c = defaultdict(list)
    parent_checkpoints = set([c['parent'] for c in r.values() if c['parent']])

    for k, v in r.items():
        if k in parent_checkpoints:
            continue
        for s in v['sources']:
            c[s].append(k)  # маппинг "имя камеры": "id кпп (не родительского)"

    if c.get(camera_name):
        # считаем за актуальный последний кпп из списка (на случай, если их будет несколько)
        cid = c[camera_name][-1]
        checkpoint, created = Checkpoint.objects.get_or_create(pk=cid, defaults={'name': r[cid]['name']})
        if checkpoint.name != r[cid]['name']:
            log.info(f'checkpoint {checkpoint} changed name to {r[cid]["name"]}')
            checkpoint.name = r[cid]['name']
            checkpoint.save()
            return checkpoint


class WebcamWebhook(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        log.debug(f'webcam rq {request.body}')
        body = json.loads(request.body)
        pl = json.loads(request.body)['body']

        if cache.get(body['id']):
            return HttpResponse()

        # идентифицируем камеру только по имени
        camera, created = Camera.objects.update_or_create(location=pl['source'], defaults={
            'lat': pl['latlng'][0],
            'lon': pl['latlng'][1]
        })

        # узнаем, с каким КПП она связана (если не связана в api - деассоциируем у нас)
        cp = fetch_camera_checkpoint(camera.location)
        if cp:
            if camera.checkpoint != cp:
                log.info(f'camera {camera} moved from {camera.checkpoint} to {cp}')
                camera.checkpoint = cp
                camera.save()
        else:
            log.info(f'camera {camera} dissociated with checkpoint {camera.checkpoint}')
            camera.checkpoint = None
            camera.save()

        vehicle, created = Vehicle.objects.update_or_create(grnz=pl['number'], defaults={'model': pl.get('mark')})
        if created:
            log.info(f'vehicle created {vehicle}')

        capture, created = CameraCapture.objects.update_or_create(
            id=pl['raw']['event']['uuid'],
            defaults={
                # перезаписываем дату создания чтобы приложение видело новые изменения вверху
                'add_date': datetime.utcnow(),
                'date': datetime.strptime(pl['raw']['event']['time'], '%Y-%m-%dT%H:%M:%S.%f%z'),
                'camera': camera,
                'vehicle': vehicle,
                'raw_data': body
            }
        )
        if created:
            log.info(f'capture created {capture}')

        for v in pl.get('iins', []):
            # assert is_iin(v)
            person, created = Person.objects.get_or_create(
                doc_id=v['iin'],
                citizenship__in=CITIZENSHIPS_KZ,
                defaults={"citizenship": Country.objects.get(pk=CITIZENSHIP_KZ)}
            )

            capture.persons.add(person)

            if created:
                log.info(f'person created {person}')
                person.update_from_dmed()

        # рассылаем уведомление по вебсокетам
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            CameraConsumer.GROUP_NAME_TEMPLATE.format(camera.id),
            {
                'type': 'notify_about_event',
                'payload': {'event': 'refresh', 'type': 'CameraCapture'}
            }
        )

        cache.set(body['id'], body, 60*60*24)
        return HttpResponse()
