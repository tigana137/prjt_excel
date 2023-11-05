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
