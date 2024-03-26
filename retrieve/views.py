# Import Django's JSON encoder
from django.db.models.functions import TruncMonth
from django.db.models import Q
from django.db.models.functions import Length
from thefuzz import fuzz
from django.db.models import Sum
import time
from datetime import date
import json
from rest_framework.decorators import api_view
import requests
import base64
from django.http import JsonResponse
from rest_framework.response import Response
from retrieve.functions import merge_arrays, search_by_fuzzy_algo, search_elv_by_date, search_elv_custom_sql_query, set_multiple_names


from x.models import AdminEcoledata, AdminElvs, Del1, Dre, Elvsprep, levelstat
from x.serializers import AdminEcoledataSerializer, levelstatSerializer


@api_view(['GET'])
def getDel1s(request):
    start_time = time.time()
    "http://localhost:80/api/retrieve/getDel1s/"
    dre_id = 84
    dre = Dre.objects.filter(id=dre_id).first()
    del1s = dre.Del1s.all()
    del1s_dic = {del1.id: del1.name for del1 in del1s}

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")

    return Response(del1s_dic)


@api_view(['GET'])
def getEcoles(request):
    "http://localhost:80/api/retrieve/getEcoles/"
    start_time = time.time()

    dre_id = 84
    del1s = Del1.objects.filter(dre_id=dre_id)
    ecoles_dic = {}
    for del1 in del1s:
        del1_ecoles = del1.ecoles.all()
        ecoles_serialized = AdminEcoledataSerializer(
            del1_ecoles, many=True).data
        del1_ecoles_dic = {}
        for ecole in ecoles_serialized:
            sid = ecole['sid']
            ecole['name'] = ecole['ministre_school_name']
            del1_ecoles_dic[sid] = ecole
        ecoles_dic[del1.id] = del1_ecoles_dic

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
    return Response(ecoles_dic)


@api_view(['GET'])
def getLevelStat(request):
    "http://localhost:80/api/retrieve/getLevelStat/"
    dre_id = 84
    stats = levelstat.objects.filter(lid__startswith=dre_id)
    statss = {}
    start_time = time.time()

    for stat in stats:
        statss[stat.lid] = {
            "nbr_elvs": stat.nbr_elvs,
            "nbr_classes": stat.nbr_classes,
            "nbr_leaving": stat.nbr_leaving,
            "nbr_comming": stat.nbr_comming,
        }

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
    return Response(statss)


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
                "name": ecole["school_name"],
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
def searchElv(request, name=None, birth_date=None):
    "http://localhost:80/api/retrieve/getElv/byname/ابتهال مريم"

    result = []

    if birth_date:
        result = search_elv_by_date(birth_date)

    if name:
        result1 = []  # na7eha ki traj3 l zouz loutanin
        # possible_names_versions = set_multiple_names(name)
        # result1 = search_elv_custom_sql_query(possible_names_versions)
        elvs_name = list(AdminElvs.objects.all().values(
            'uid',  'nom_prenom', 'nom_pere', 'date_naissance', 'ecole__school_name'))
        elvs_name = ([elv['uid'], elv['nom_prenom'], elv['nom_pere'], elv['date_naissance'],
                     elv['ecole__school_name'],] for elv in elvs_name)
        result2 = search_by_fuzzy_algo(elvs_name, searched_name=name)
        result = merge_arrays(result1, result2)
    return Response(result)


@api_view(['GET'])
def test(request, valeur=None):
    "http://localhost:80/api/retrieve/test/"

    return Response(True)
