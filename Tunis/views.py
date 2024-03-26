# Import Django's JSON encoder
from django.db.models import Max
from django.db.models import Min
import time
from rest_framework.decorators import api_view
import requests

from rest_framework.response import Response
from Tunis.bulkCreate_classes_elves import bulkcreate_Classes_of_1ecole, bulkcreate_Eleves_of_1ecole, get_nbr_classes_and_elvs
from Tunis.functions import extract_cnte_id, extract_ecoles_of_dre_info
from Tunis.models import ClassTunis, DreTunis, EcolesTunis, ElvsTunis, ElvsTunis
from Tunis.strict_conditions import Verify_Dre_exits, Verify_both_cnte_ids_same, Verify_len_dres_same, Verify_number_of_classes_matches, Verify_number_of_elvs_matches
from Tunis.utils import send_get_request
from django.db import transaction
from bs4 import BeautifulSoup as bs

import re

from retrieve.functions import search_by_fuzzy_algo, search_elv_by_date
from x.functions import CustomError, get_clean_name


def check_dre_db_good():
    print('checking if all dres exists with the same name and cnte_id (exp : sousse= 7 ) ')

    request = requests.session()
    cnte_url = "http://www.ent.cnte.tn/ent/"

    soup = send_get_request(url=cnte_url, request=request, decode=False)

    request.close()
    list_element = soup.find('ul', {'id': 'menu-accordeon'})
    links = list_element.find_all('a', {'id': 'Servs'})

    Verify_len_dres_same(dres_count_in_soup=len(links))

    for link in links:
        dre_name = link.text.strip()
        db_dre_id_in_cnte = Verify_Dre_exits(dre_name)

        dre_cnte_id_in_function = link["onclick"]
        dre_cnte_id = extract_cnte_id(dre_cnte_id_in_function)

        Verify_both_cnte_ids_same(db_dre_id_in_cnte, dre_cnte_id)

    print('Done ')


def update_ecoles_info():   # tmchi l cnte w extracti l name,principal w slug
    "http://localhost:80/api/Tunis/test/"
    print('updating all ecoles : name , slug')
    print('ps : w8 5s after each iteration of wileya')

    request = requests.session()
    dres = DreTunis.objects.all().values('id', 'name', 'dre_id_in_cnte')
    try:
        for dre in dres:
            print('traitment de dre : ', dre['name'])

            url = "http://www.ent.cnte.tn/ent/lireJson.php?gov=" + \
                str(dre['dre_id_in_cnte'])
            soup = send_get_request(url=url, request=request, decode=False)

            ecoles = extract_ecoles_of_dre_info(soup=soup, dre=dre)

            with transaction.atomic():
                EcolesTunis.objects.bulk_create(
                    ecoles, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=["school_name", "school_name", "principal", "slug"])

            print('✓ extraction of dre succefuly now sleeping for 5')
            time.sleep(5)

    finally:
        request.close()

    return Response(True)


@api_view(['GET'])
def test(request, valeur=None):
    "http://localhost:80/api/Tunis/test/"
    # check_dre_db_good()
    # update_ecoles_info()

    return Response(True)


@api_view(['GET'])
def test(request, valeur=None):
    "http://localhost:80/api/Tunis/test/"

    request = requests.session()
    prev = 1859+177+60
    for i in range(50):
        ecoles = EcolesTunis.objects.filter(extracted_from=False).order_by('?')
        ecole = ecoles.first() 

        # ecole = EcolesTunis.objects.get(sid=212009) 
   
        try: 
            print('traitment of Ecole sid :', str(ecole.sid))
            (nbr_class, nbr_elvs) = get_nbr_classes_and_elvs(
                ecole_slang=ecole.slug, request=request)

            bulkcreate_Classes_of_1ecole(ecole, request, nbr_class)
 
            # ! u sleep for 1 sec in each class extract
            bulkcreate_Eleves_of_1ecole(ecole, request, nbr_elvs)

            ecole.extracted_from = True
            ecole.save()
            print('\ntraitment of Ecole ran smoothly ✓ ✓ ✓ ✓ ✓ ✓\n')
        except KeyboardInterrupt:
            request.close()
        finally:
            request.close()

        allecoles_treated = EcolesTunis.objects.filter(extracted_from=True).count()
        print('ecoles treated today = ', str(allecoles_treated-prev),'\n\n')
        time.sleep(10)
    
    return Response(True)




@api_view(['GET'])
def searchElv(request, name=None):
    "http://localhost:80/api/Tunis/searchElv/مريم هلالي"

    result = []

    elvs_name = list(ElvsTunis.objects.all().values(
        'uid',  'nom_prenom', 'classe__class_name','classe__level','ecole__school_name'))
    elvs_name = ([elv['uid'], elv['nom_prenom'], elv['classe__class_name'], elv['classe__level'],
                    elv['ecole__school_name'],] for elv in elvs_name)
    result = search_by_fuzzy_algo(elvs_name, searched_name=name)

    return Response(result)
 