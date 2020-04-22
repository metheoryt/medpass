import logging

import requests
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.views import APIView

from core.models import Camera, Checkpoint

log = logging.getLogger(__name__)


class ImportCheckpoints(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Импортирует КПП из https://application-rubezh.egsv.kz/checkpoints?sources=1
        :param request:
        :param format:
        :return:
        """

        r = requests.get(
            'https://application-rubezh.egsv.kz/checkpoints?sources=1'
        ).json()['checkpoints']

        parents = set([c['parent'] for c in r.values() if c['parent']])

        created_checkpoints = []
        created_cameras = []
        for cid, c in r.items():
            if cid in parents:
                # игнорируем родительские категории
                log.debug(f'ignoring {cid} - it is parent')
                continue

            checkpoint, created = Checkpoint.objects.update_or_create(pk=cid, defaults={'name': c['name']})
            if created:
                log.info(f'created checkpoint {checkpoint}')
                created_checkpoints.append(checkpoint)

            for s in c['sources']:
                camera, created = Camera.objects.get_or_create(location=s)
                if created:
                    created_cameras.append(camera)
                    log.info(f'created camera {camera} for checkpoint {checkpoint}')
                checkpoint.cameras.add(camera)

        return render(request, 'checkpoints-import.html', context={
            'checkpoints': created_checkpoints,
            'cameras': created_cameras
        })
