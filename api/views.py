import logging

from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.utils import json
from rest_framework.views import APIView

from core.models import Camera, CameraCapture, Vehicle, Person, CITIZENSHIPS_KZ, CITIZENSHIP_KZ

log = logging.getLogger(__name__)


class WebcamWebhook(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        log.debug(f'webcam rq {request.body}')
        body = json.loads(request.body)
        pl = json.loads(request.body)['body']

        if cache.get(body['id']):  #
            return HttpResponse()

        camera, created = Camera.objects.update_or_create(
            id=pl['raw']['event']['origin'],
            defaults={
                'lat': pl['latlng'][0],
                'lon': pl['latlng'][1],
                'location': pl['source']
            }
        )
        if created:
            log.info(f'{camera} created')

        if camera.checkpoint:
            # сохраняем захваты только с камер, привязанных к КПП
            vehicle, created = Vehicle.objects.update_or_create(grnz=pl['number'], defaults={'model': pl.get('mark')})
            if created:
                log.info(f'{vehicle} created')

            capture, created = CameraCapture.objects.update_or_create(
                id=pl['raw']['event']['uuid'], defaults={
                'date': pl['raw']['event']['time'],
                'camera': camera,
                'vehicle': vehicle,
                'raw_data': body
            })
            if created:
                log.info(f'{capture} created')

            checkpoint_pass = capture.create_or_update_checkpoint_pass(self.request.user)

            for v in pl.get('iins', []):
                person, created = Person.objects.get_or_create(
                    doc_id=v['iin'],
                    citizenship__in=CITIZENSHIPS_KZ,
                    defaults={"citizenship": CITIZENSHIP_KZ}
                )
                if created:
                    log.info(f'{person} created')
                    person.update_from_dmed()
                checkpoint_pass.persons.add(person)
            else:
                checkpoint_pass.save()

        cache.set(body['id'], body, 60*60*24)
        return HttpResponse()
