from django.forms import ValidationError
from rest_framework import status

from rest_framework.decorators import api_view

from rest_framework.response import Response
from django.http import HttpResponse
from excel.ExcelAlgo import initiate_Excel
from excel.conditions import transferElv_condition
from excel.functions import adjust_levelstat, create_excelsheetRow
from excelpremiere.conditions import transferElv_conditionPremiere
from excelpremiere.functions import cancel_excelsheetRowPremiere, create_excelsheetRowPremiere

from x.models import AdminEcoledata, AdminElvs, Del1, Elvsprep


# Create your views here.
# l page t3 l i3tiradhat nrmlment bch tkoun 3ndha durre mou3ayna sinn b3d me3atch famma i3tiradhat donc twalli inavaible 5atr me3atch fama i3tiradhat 
# w zid l eleve t3 premiere anner iwalliw avaible w ijiw fil page t3hom donc is2l w9teh ybdew y5dmou beha w w9teh youfa w9tha w si l premier fil site me iji
# dima ken b3d me toufa l i3tiradhat walla mouch bidharoura tnajjm tji fil wost

# asm3 ken l excel t3 l nrmal wel premiere kifkif 9oullou ken t7b n3ml w7da for premiere 5atr dhahrli l resource te3ou m7douda heka 3lh y3ml fihom l zouz
# fard template

# thabt e5i t7dhiri 3ndouch nom parent walle


@api_view(['GET'])
def GetElvpremiere(request, uid):
    eleve_premiere = Elvsprep.objects.filter(uid=uid).first()

    if not eleve_premiere : 
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    data = {
        'uid': '0' + str(eleve_premiere.uid),
        'nom': eleve_premiere.nom,
        'prenom': eleve_premiere.prenom,
        'date_naissance': eleve_premiere.date_naissance,
        'prev_ecole': eleve_premiere.ecole.ministre_school_name,
        'prev_ecole_id': eleve_premiere.ecole.sid,
        'decision': 'مع الموافقة',
    }
    return Response(data)


@api_view(['POST'])
def transferElvPremiere(request):
    # jwt_payload = verify_jwt(request)
    #
    # dre_id = jwt_payload['dre_id']
    dre_id = "84"
    try:
        (prev_ecole_id, next_ecole_id) = transferElv_conditionPremiere(request.data)
    except ValidationError:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    adjust_levelstat(prev_ecole_id, next_ecole_id,level= 1,dre_id=dre_id,cancel=False)

    create_excelsheetRowPremiere(request.data,dre_id)

    return Response({"response": True}, status=status.HTTP_200_OK)


@api_view(['POST'])
def cancel_transferElvPremiere(request):
    # jwt_payload = verify_jwt(request)
    #
    # dre_id = jwt_payload['dre_id']
    dre_id = "84"

    try:
        (prev_ecole_id, next_ecole_id) = transferElv_conditionPremiere(request.data)
    except ValidationError:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)


    adjust_levelstat(prev_ecole_id,next_ecole_id, level=1,dre_id=dre_id,cancel=True)

    cancel_excelsheetRowPremiere(request.data,dre_id)

    return Response({"response":True})


