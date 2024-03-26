from django.urls import path
from . import views

urlpatterns = [
       path('testSignal/',
              views.testSignal, name='testSignal'),
       path('verifyDreCredentials/',
              views.verifyDreCredentials, name='verifyDreCredentials'),
       path('signup/',
              views.signup, name='signup'),
       path('signin/',
              views.signin, name='signin'),
       path('logout/',
              views.logout, name='logout'),

]