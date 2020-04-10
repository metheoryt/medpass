from django.urls import path, include
from rest_framework_nested import routers
from . import viewsets


# перспектива мединспектора
cp_router = routers.SimpleRouter()
cp_router.register(r'passes', viewsets.InspectorCheckpointPassViewSet, basename='inspector-checkpoint-pass')
cp_router.register(r'captures', viewsets.CheckpointCameraCaptureViewSet, basename='inspector-checkpoint-capture')
pass_router = routers.NestedSimpleRouter(cp_router, r'passes', lookup='checkpoint_pass')
pass_router.register(r'persons', viewsets.CheckpointPassPersonViewSet, basename='checkpoint-pass-person')

# перспектива страны
router = routers.SimpleRouter()
router.register(r'countries', viewsets.CountryViewSet)
router.register(r'regions', viewsets.RegionViewSet)
router.register(r'checkpoints', viewsets.CheckpointViewSet)
router.register(r'vehicles', viewsets.VehicleViewSet)

countries_router = routers.NestedSimpleRouter(router, r'countries', lookup='country')
countries_router.register(r'persons', viewsets.CountryPersonViewSet, basename='country-person')

persons_router = routers.NestedSimpleRouter(countries_router, r'persons', lookup='person')
persons_router.register(r'markers', viewsets.CountryPersonMarkerViewSet, basename='country-person-marker')


# noinspection PyTypeChecker
urlpatterns = [
    path('inspector',
         viewsets.InspectorViewSet.as_view(dict(get='retrieve', put='update', patch='partial_update')), ),
    path('inspector/checkpoint',
         viewsets.InspectorCheckpointViewSet.as_view(dict(get='retrieve', put='update', patch='partial_update'))),
    path('inspector/checkpoint/', include(cp_router.urls)),
    path('inspector/checkpoint/', include(pass_router.urls)),
    path('', include(router.urls)),
    path('', include(countries_router.urls)),
    path('', include(persons_router.urls)),
]
