import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class CheckpointConsumer(WebsocketConsumer):
    GROUP_NAME_TEMPLATE = 'checkpoint_{}'

    def connect(self):
        self.accept()
        self.checkpoint_id = self.scope['url_route']['kwargs']['checkpoint_id']
        self.group_name = self.GROUP_NAME_TEMPLATE.format(self.checkpoint_id)
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
