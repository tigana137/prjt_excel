from django.urls import path
from . import views

urlpatterns = [
    path('testSignal/',
         views.testSignal, name='testSignal'),
    path('GetCapatcha/',
         views.GetCapatcha, name='GetCapatcha'),
    path('VerifyCapatcha/<str:code>',
         views.VerifyCapatcha, name='VerifyCapatcha'),
    path('getmoudirins/',
         views.getMoudirins, name='getMoudirins'),
    path('testAdmin/<str:code>/',
         views.testAdmin, name='testAdmin'),
    path('getallecolesdata/',
         views.getAllEcolesData, name='getAllEcolesData'),

    path('exportDB/',
         views.exportDB, name='exportDB'),
    path('importDB/',
         views.importDB, name='importDB'),


    path('stat/',
         views.stat, name='stat'),

]


"http://localhost:80/api/x/testSignal/"
"http://localhost:80/api/x/GetCapatcha/"
"http://localhost:80/api/x/VerifyCapatcha/84"
"http://localhost:80/api/x/getmoudirins/"

"http://localhost:80/api/x/CreateExcel"


"http://localhost:80/api/x/testAdmin/54"
