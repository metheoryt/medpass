from django.contrib import admin
from django.urls import path
from django.urls import include

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'persons', views.PersonViewSet)
router.register(r'dmed-info', views.DMEDPersonInfoViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]
