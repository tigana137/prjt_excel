from django.urls import path
from . import views


urlpatterns = [
    path('test/<str:valeur>',
         views.test, name='test'),
    path('test/',
         views.test, name='test'),

    path('getLevelStat/',
         views.getLevelStat, name='getLevelStat'),
    path('getDel1s/',
         views.getDel1s, name='getDel1s'),
    path('getEcoles/',
         views.getEcoles, name='getEcoles'),
    path('getallecolesdata/',
         views.getAllEcolesData, name='getAllEcolesData'),
    path('searchElv/byname/<str:name>',
         views.searchElv, name='searchElv'),
    path('searchElv/bydate/<str:birth_date>',
         views.searchElv, name='searchElv'),

]


"http://localhost:80/api/retrieve/searchElv/qsdqsd"
