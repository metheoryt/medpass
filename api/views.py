import logging

from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.utils import json
from rest_framework.views import APIView

from core.models import Camera, CameraCapture, Vehicle

log = logging.getLogger(__name__)


class WebcamWebhook(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        log.info(f'webcam rq: {request.body[:10_000]}')
        body = json.loads(request.body)
        pl = json.loads(request.body)['body']

        if cache.get(body['id']):  # защита от повторных запросов
            return HttpResponse()

        camera, created = Camera.objects.update_or_create(
            id=pl['raw']['event']['origin'],
            defaults={
                'lat': pl['latlng'][0],
                'lon': pl['latlng'][1],
                'location': pl['source']
            }
        )

        if camera.checkpoint:
            # сохраняем захваты только с камер, привязанных к КПП
            vehicle, created = Vehicle.objects.update_or_create(grnz=pl['number'], defaults={'model': pl.get('mark')})

            CameraCapture.objects.create(
                id=pl['raw']['event']['uuid'],
                date=pl['raw']['event']['time'],
                vehicle=vehicle,
                camera=camera,
                raw_data=body
            )

        cache.set(body['id'], body, 60*60*24)
        return HttpResponse()
