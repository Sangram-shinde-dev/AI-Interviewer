from django.urls import re_path
from .consumers import AudioInterviewConsumer

websocket_urlpatterns = [
    re_path(r"ws/interview/", AudioInterviewConsumer.as_asgi()),
]
