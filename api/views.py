import logging
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.utils import json
from rest_framework.views import APIView

from api2.consumers import CheckpointConsumer
from core.models import Camera, CameraCapture, Vehicle, Person, CITIZENSHIPS_KZ, CITIZENSHIP_KZ, Country

log = logging.getLogger(__name__)


class WebcamWebhook(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        log.debug(f'webcam rq {request.body}')
        body = json.loads(request.body)
        pl = json.loads(request.body)['body']

        if cache.get(body['id']):
            return HttpResponse()

        camera, created = Camera.objects.update_or_create(location=pl['source'], defaults={
            'lat': pl['latlng'][0],
            'lon': pl['latlng'][1]
        })  # идентифицируем камеру только по имени
        if created:
            log.info(f'camera created {camera}')

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

        if camera.checkpoint:
            # рассылаем уведомление по вебсокетам
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                CheckpointConsumer.GROUP_NAME_TEMPLATE.format(camera.checkpoint.id),
                {
                    'type': 'notify_about_event',
                    'payload': {'event': 'refresh', 'type': 'CameraCapture'}
                }
            )

        cache.set(body['id'], body, 60*60*24)
        return HttpResponse()
