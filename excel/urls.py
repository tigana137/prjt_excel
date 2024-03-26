from django.urls import path
from . import views

urlpatterns = [
     path('Test/',
         views.Test, name='test'),
     path('GetDel1/',
         views.GetDel1, name='GetDel1'),
     path('GetEcoles/',
         views.GetEcoles, name='GetEcoles'),
     path('Getexcelrows/<int:page>',  
         views.GetExcelRows, name='GetExcelRows'),
     path('GetElv/<str:uid>',  
         views.GetElv, name='GetElv'),
     path('transferElv/',
         views.transferElv, name='transferElv'),
     path('cancel_transferElv/',
         views.cancel_transferElv, name='cancel_transferElv'),
     path('CreateExcel/',
         views.CreateExcel, name='CreateExcel'),

     path('check_nbr_elv_post_transfer/',
         views.check_nbr_elv_post_transfer, name='check_nbr_elv_post_transfer'),
]
