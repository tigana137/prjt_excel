from rest_framework.decorators import api_view
import requests
import base64
from django.http import JsonResponse
from rest_framework.response import Response
from django.http import HttpResponse
from x.ExcelAlgo import initiate_Excel
from x.Update_ecol_elv import create_AdminElvs2

from x.models import AdminEcoledata2, AdminElvs, Del1







request2 = requests.session()





@api_view(['GET'])
def GetCapatcha(request):
    url = "http://admin.inscription.education.tn/"
    request2.get(url=url)

    url_img = "http://admin.inscription.education.tn/inclure/img.php"
    img = request2.get(url=url_img)

    # Assuming you have the binary image data in 'image_data'
    image_data_base64 = base64.b64encode(img.content).decode('utf-8')

    # Create a JSON response with the base64-encoded image
    response_data = {'image_data': image_data_base64}

    return JsonResponse(response_data)


@api_view(['GET'])
def VerifyCapatcha(request, code):
    url = "http://admin.inscription.education.tn/"
    payload = {"login": "Sousse",
               "pwd": "VGhNL85Qa",
               "secure": code,
               "auth": "",
               }
    response = request2.post(url=url, data=payload)
    # response.headers
    if not ("http://admin.inscription.education.tn/ministere/index.php" in response.url):
        return Response(False)
    #create_AdminElvs2(request2)
    return Response(True)


@api_view(['GET'])
def GetEDel1(request):
    Del1s = Del1.objects.filter(
        id__startswith=84).values_list('name', flat=True)
    return Response(Del1s)


@api_view(['GET'])
def GetEcoles(request):
    ecoles_dic = {}
    ecoles = AdminEcoledata2.objects.filter(sid__startswith=84)
    for ecole in ecoles:
        try:
            ecoles_dic[ecole.del1.name].append(ecole.school_name)
        except:
            ecoles_dic[ecole.del1.name] = [ecole.school_name]
    for key in ecoles_dic.keys():
        ecoles_dic[key] = sorted(ecoles_dic[key])
    return Response(ecoles_dic)


@api_view(['GET'])
def GetElv(request, uid):
    try:
        eleve = AdminElvs.objects.get(uid=uid)
        data = {
            'uid': '0'+str(eleve.uid),
            'nom_prenom': eleve.nom_prenom,
            'nom_pere': eleve.nom_pere,
            'date_naissance': eleve.date_naissance,
            'prev_ecole': eleve.ecole.school_name,
            'decision': 'مع الموافقة',
        }
        return Response(data)
    except AdminElvs.DoesNotExist:
        return Response(False)


@api_view(['POST'])
def CreateExcel(request):
    workbook, FileName = initiate_Excel(request.data)
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
    # Save the workbook to the response
    workbook.save(response)
    response['Content-Disposition'] = 'attachment; filename='+FileName+'.xlsx'
    return response


@api_view(['GET'])
def testAdmin(request, code):

    return Response(True)
