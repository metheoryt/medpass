import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class CameraConsumer(WebsocketConsumer):
    GROUP_NAME_TEMPLATE = 'checkpoint_camera_{}'

    def connect(self):
        self.accept()
        self.camera_id = self.scope['url_route']['kwargs']['camera_id']
        self.group_name = self.GROUP_NAME_TEMPLATE.format(self.camera_id)
        # добавляем в группу слушателей событий с этого чекпоинта
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

    def disconnect(self, close_code):
        # удаляем из группы
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=json.dumps({'event': 'pong'}))

    def notify_about_event(self, event):
        self.send(text_data=json.dumps(event['payload']))
