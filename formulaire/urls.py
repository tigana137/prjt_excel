
from django.urls import path
from . import views

urlpatterns = [

    path('searchElv/byname/<str:name>',
         views.searchElv, name='searchElv'),
    path('searchElv/bydate/<str:birth_date>',
         views.searchElv, name='searchElv'),

]