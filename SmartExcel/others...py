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
from x.Update_ecol_elv import get_clean_name
from x.UpdatesPrincipals import update_principals
from x.exportModels import exportAdminEcoledata, exportAdminElvs, exportDel1, exportDre, exportElvsprep, exportlevelstat
from x.importModels import importAdminEcoledata, importAdminElvs, importDel1, importDre, importElvsprep, importlevelstat


from x.models import AdminEcoledata, AdminElvs, Del1, Dre, Elvsprep, levelstat, names
from x.serializers import AdminEcoledataSerializer, levelstatSerializer



######### some stats #########

def calculate_count_most_elvs_with_same_date():  # highest 100 counts
    from django.db.models import Count
    date_counts = AdminElvs.objects.values(
        'date_naissance').annotate(count=Count('date_naissance')).order_by('-count')[:100]

    for i in range(100):
        print(
            f'{"0" if i<9 else ""}{i+1} date= {date_counts[i]["date_naissance"]}:  {date_counts[i]["count"]}')


def calculate_count_most_elvs_with_same_month():  # highest 100 counts
    from django.db.models import Count
    month_counts = AdminElvs.objects.annotate(month=TruncMonth('date_naissance')).values(
        'month').annotate(count=Count('month')).order_by('-count')[:100]

    for i in range(100):
        print(
            f'{"0" if i<9 else ""}{i+1} date= {month_counts[i]["month"]}:  {month_counts[i]["count"]}')


def get_shortest_names():   # highest 100 counts
    shortest_names = AdminElvs.objects.annotate(
        nom_prenom_length=Length('nom_prenom')).order_by('nom_prenom_length')[:100]
    shortest_names_list = [(obj.nom_prenom, len(obj.nom_prenom))
                           for obj in shortest_names]
    return shortest_names_list


###########################
#   hedhi 3mltha 9bal me wallit t3ml clean_name kol me t3ml l scrape w t7ot esemi l tlmetha f db
#   hiya te5ou esemi l tlemtha l kol (supposée untreated) w te5ou mnhom awil kelma m3neha mn 9bal l espace 3ala esses l esm
#   t3ml set() bch te5ou l unique esemi w t3tik l len w b3d l len ki t3ml l function get_clean_name
#   k 3mltha 9bal hedha chtl3t resultat : unique name b4 treatment (from 81.142 total elvs name) was 11.120 and after was 2312

def create_names_from_scratch(): 
    names.objects.all().delete()

    allnames = set(AdminElvs.objects.all(
    ).values_list('nom_prenom', flat=True))
    print("len of all names : ", len(allnames))
    allnamesonly = []
    for name in allnames:
        nom_seulement = ""
        try:
            nom_seulement = name.split()[0]
        except:
            print(name, " famma name vid walla mefih 7atta espace")
        if nom_seulement != "":
            allnamesonly.append(nom_seulement)

    unique_names = set(allnamesonly)
    print("len of unique names (pre-traitment): ", len(unique_names))

    names_model = []
    for nameonly in unique_names:
        names_model.append(names(name=nameonly))
    names.objects.bulk_create(names_model)

    print("create_unique_names done")


def delete_prev_names_create_post_treatment_unique_names():

    def bulk_create_names(post_treatment_names):
        names.objects.all().delete()

        unique_names = set(post_treatment_names)
        print('len of all names post treatment : '+str(len(unique_names)))
        names_model = []
        for nameonly in unique_names:
            names_model.append(names(name=nameonly))
        names.objects.bulk_create(names_model)

    allnames = list(names.objects.all().values_list('name', flat=True))
    print('len of all names untreated : '+str(len(allnames)))

    for i in range(len(allnames)):
        allnames[i] = get_clean_name(allnames[i])

    bulk_create_names(allnames)

    print('treatment + bulk creating is done ')


def excute():
    create_names_from_scratch()
    delete_prev_names_create_post_treatment_unique_names()


