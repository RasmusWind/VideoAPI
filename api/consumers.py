import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .base_serializers import UserSerializer

class BaseConsumer(WebsocketConsumer):

    def get_sender_user(self, user_id):
        return User.objects.get(pk=user_id)

    def connect(self):
        user_id = self.scope['user']
        user = self.get_sender_user(user_id.id)
        print()
        print(user.username)
        print()
        self.room_group_name = user.username

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
   

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        sender = self.get_sender_user(self.scope["user"].id)
        message = text_data_json['message']
        receiver = text_data_json["receiver"]

        async_to_sync(self.channel_layer.group_send)(
            receiver,
            {
                'type':'chat_message',
                'sender': UserSerializer(instance=sender).data,
                'message':message
            }
        )

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        self.send(text_data=json.dumps({
            'sender':sender,
            'message':message
        }))