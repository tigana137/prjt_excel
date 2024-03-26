from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
import json
import re
from rest_framework import status

from bidict import bidict
from django.db import IntegrityError
from rest_framework.decorators import api_view
import requests
import base64
from django.http import JsonResponse
from rest_framework.response import Response
from django.http import HttpResponse
from x.AnnualExcel import annualexcel
from x.Update_ecol_elv import create_AdminEcole_data, create_AdminElvs, create_Elvpremiere, create_Elvsprep

from x.models import AdminEcoledata, AdminElvs, Del1, Dre, Elvsprep

from rest_framework.exceptions import ValidationError 

from bs4 import BeautifulSoup as bs



def transferElv_conditionPremiere(request_data):
    if not 'prev_ecole_id' in request_data or not 'next_ecole' in request_data :
        raise ValidationError()
    
    try:
        prev_ecole_id = int(request_data["prev_ecole_id"])
        next_ecole_id = int(request_data["next_ecole_id"])
    except ValueError:
        raise ValidationError()

    
    return (prev_ecole_id,next_ecole_id)