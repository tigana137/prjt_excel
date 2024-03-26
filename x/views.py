<<<<<<< HEAD
# Import Django's JSON encoder
from django.db.models.functions import TruncMonth
from django.db.models import Q
from django.db.models.functions import Length
from thefuzz import fuzz
from django.db.models import Sum
import time
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
import json
from bidict import bidict
from rest_framework.decorators import api_view
import requests
import base64
from django.http import JsonResponse
from rest_framework.response import Response
from excel.models import excelsheets
from x.Update_ecol_elv import create_AdminEcole_data, create_AdminElvs, create_Elvpremiere, create_Elvsprep
from x.UpdatesPrincipals import update_principals
from x.exportModels import exportAdminEcoledata, exportAdminElvs, exportDel1, exportDre, exportElvsprep, exportlevelstat
from x.functions import CustomError, get_clean_name
from x.importModels import importAdminEcoledata, importAdminElvs, importDel1, importDre, importElvsprep, importlevelstat
from django.db import transaction


from x.models import AdminEcoledata, AdminElvs, Del1, DirtyNames, Dre, Elvsprep, Tuniselvs, levelstat
from x.serializers import AdminEcoledataSerializer, levelstatSerializer


sids_to_replace = bidict({"842911": "842811",
                          "842913": "842813",
                          "842922": "842822",
                          "842923": "842823",
                          "842924": "842824",
                          "842912": "842812",
                          "842914": "842814"
                          })

request2 = requests.session()


@api_view(['GET'])
def testSignal(request):
    "http://localhost:80/api/x/testSignal/"

    return Response(True)


@api_view(['GET'])
def GetCapatcha(request):
    url = "https://suivisms.cnte.tn/"
    request2.get(url=url)

    try:
        url_img = "https://suivisms.cnte.tn/inclure/img.php"
        img = request2.get(url=url_img)
    except Exception as e:
        print(e)
        raise CustomError("fama mochkla k jit te5ou fil taswira")

    # Assuming you have the binary image data in 'image_data'
    image_data_base64 = base64.b64encode(img.content).decode('utf-8')

    # Create a JSON response with the base64-encoded image
    response_data = {'image_data': image_data_base64}

    return JsonResponse(response_data)


@api_view(['GET'])
def VerifyCapatcha(request, code):
    url = "https://suivisms.cnte.tn/"
    payload = {"login": "user8420",
               "pwd": "78b9adE48U",
               "secure": code,
               "auth": "",
               }

    response = request2.post(url=url, data=payload)

    # response.headers
    if not ("https://suivisms.cnte.tn/" in response.url):
        print(response.url)
        return Response(False)

    # create_AdminEcole_data(request2)
    # create_AdminElvs(request2)
    # create_Elvsprep(request2)
    # create_Elvpremiere(request2)
    return Response(True)


@api_view(['GET'])
def getAllEcolesData(request):
    start_time = time.time()
    levels = levelstat.objects.filter(lid__startswith=84)
    levels = {level.lid: {
        "nbr_elvs": level.nbr_elvs,
        "nbr_classes": level.nbr_classes,
        "nbr_leaving": level.nbr_leaving,
        "nbr_comming": level.nbr_comming,
    }for level in levels}

    dic = {}
    dels = Del1.objects.filter(id__startswith=84).exclude(id=8498)
    for del1 in dels:
        dic[del1.id] = {"name": del1.name, }
        dic[del1.id]["ecoles"] = {}
        ecole_dic = {}
        ecoles = del1.ecoles.all().values(
            "sid", "school_name", "ministre_school_name", "principal")
        levels_str = ["premiere", "deuxieme", "troisieme",
                      "quatrieme", "cinquieme", "sixieme"]

        for ecole in ecoles:
            ecole_dic[ecole["sid"]] = {
                "school_name": ecole["school_name"],
                "name": ecole["ministre_school_name"],
                "principal": ecole["principal"],
            }
            for i in range(6):
                ecole_dic[ecole["sid"]][levels_str[i]
                                        ] = levels[int(str(ecole["sid"])+str(i+1))]

        dic[del1.id]["ecoles"] = ecole_dic

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
    return Response(dic)


@api_view(['GET'])
def testAdmin(request, code=None):

    return Response(True)


@api_view(['GET'])
def getMoudirins(request):
    update_principals()

    return Response(True)


@api_view(['GET'])
def exportDB(request):
    "http://localhost:80/api/x/exportDB"
    # exportDre()
    # exportDel1()
    # exportlevelstat()
    # exportAdminEcoledata()
    # exportAdminElvs()
    # exportElvsprep()
    return Response(True)


@api_view(['GET'])
def importDB(request):
    "http://localhost:80/api/x/importDB"
    AdminElvs.objects.all().delete()
    Elvsprep.objects.all().delete()
    importDre()
    importDel1()
    importlevelstat()
    importAdminEcoledata()
    importAdminElvs()
    importElvsprep()
    return Response(True)


@api_view(['GET'])
def stat(request):
    "http://localhost:80/api/x/stat"
    # fkra o5ra f stat a3ml total ecoles f soussa w total etatiq w total privee
    #  another one maybe total nbr elvs etatiq w total privee
    dre_id = 84
    nbr_tranfers = excelsheets.objects.filter(dre__id=dre_id).count()

    return Response(nbr_tranfers)




=======
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
>>>>>>> 05b98efc67f75b0e94f2311b07801f92443b2d3a
