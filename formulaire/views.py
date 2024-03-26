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
from retrieve.functions import merge_arrays, search_by_fuzzy_algo, search_elv_by_date, search_elv_custom_sql_query, set_multiple_names
from x.UpdatesPrincipals import update_principals
from x.models import Tuniselvs


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
        elvs_name = list(Tuniselvs.objects.all().values(
            'uid',  'nom_prenom', 'classe_id', 'ecole_id', 'ecole_name'))
        print(len(elvs_name))
        elvs_name = ([elv['uid'], elv['nom_prenom'], elv['classe_id'], elv['ecole_id'],
                     elv['ecole_name'],] for elv in elvs_name)
        result2 = search_by_fuzzy_algo(elvs_name, searched_name=name)
        result = merge_arrays(result1, result2)
        print(result)
    return Response(result)
