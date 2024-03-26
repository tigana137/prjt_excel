<<<<<<< HEAD
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
=======
from django.urls import path
from . import views

urlpatterns = [
    path('GetCapatcha/',
         views.GetCapatcha, name='GetCapatcha'),
    path('VerifyCapatcha/<str:code>',
         views.VerifyCapatcha, name='VerifyCapatcha'),
    path('GetEDel1/',
         views.GetEDel1, name='GetEDel1'),
    path('GetEcoles/',
         views.GetEcoles, name='GetEcoles'),
    path('GetElv/<str:uid>',
         views.GetElv, name='GetElv'),
    path('CreateExcel/',
         views.CreateExcel, name='CreateExcel'),

    path('testAdmin/<str:code>',
         views.testAdmin, name='testAdmin'),
]



"http://localhost:80/x/GetCapatcha/"
"http://localhost:80/x/VerifyCapatcha/84"
"http://localhost:80/x/GetEDel1"
"http://localhost:80/x/GetEcoles"

"http://localhost:80/x/GetElv/13677025561"
"http://localhost:80/x/CreateExcel"


"http://localhost:80/x/testAdmin/54"
>>>>>>> 05b98efc67f75b0e94f2311b07801f92443b2d3a
