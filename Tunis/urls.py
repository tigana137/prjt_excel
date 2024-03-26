from django.urls import path
from . import views


urlpatterns = [
    path('test/<str:valeur>',
         views.test, name='test'),
    path('test/',
         views.test, name='test'),
    path('searchElv/<str:name>',
         views.searchElv, name='searchElv'),

]


"http://localhost:80/api/Tunis/test"
