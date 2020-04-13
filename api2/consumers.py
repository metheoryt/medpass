import json
from channels.generic.websocket import WebsocketConsumer
from time import sleep
from core.models import CameraCapture


class CheckpointConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        checkpoint_id = self.scope['url_route']['kwargs']['checkpoint_id']
        last_capture = CameraCapture.objects.filter(camera__checkpoint=checkpoint_id).order_by('add_date').last()
        while True:
            sleep(2)
            _last_capture = CameraCapture.objects.filter(camera__checkpoint=checkpoint_id).order_by('add_date').last()
            if _last_capture and (not last_capture or _last_capture.add_date > last_capture.add_date):
                last_capture = _last_capture
                self.send(text_data=json.dumps({
                    'event': 'refresh',
                    'type': 'CameraCapture'
                }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
