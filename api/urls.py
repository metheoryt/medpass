from django.urls import include, path
from rest_framework import routers

from . import views, viewsets

r = routers.DefaultRouter()

r.register(r'person', viewsets.PersonViewSet)
r.register(r'checkpoint-pass', viewsets.CheckpointPassViewSet)
r.register(r'checkpoint', viewsets.CheckpointViewSet)
r.register(r'marker', viewsets.PersonMarkerViewSet)
r.register(r'region', viewsets.RegionViewSet)
r.register(r'country', viewsets.CountryViewSet)


urlpatterns = [
    path('', include(r.urls)),
    path('inspector', viewsets.InspectorViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('webhook/webcam', views.WebcamWebhook.as_view()),
]
