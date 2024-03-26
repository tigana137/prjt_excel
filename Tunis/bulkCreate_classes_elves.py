import time
from rest_framework.decorators import api_view
import requests

from rest_framework.response import Response
from Tunis.functions import extract_cnte_id, extract_ecoles_of_dre_info
from Tunis.models import ClassTunis, DreTunis, EcolesTunis, ElvsTunis
from Tunis.strict_conditions import Verify_Dre_exits, Verify_both_cnte_ids_same, Verify_len_dres_same, Verify_number_of_classes_matches, Verify_number_of_elvs_matches
from Tunis.utils import send_get_request
from django.db import transaction
from bs4 import BeautifulSoup as bs

import re

from x.functions import CustomError, get_clean_name
from django.db.models import Max


nbr_elv_with_no_uid={"nbr":1}



def get_class_name_and_level(class_name):
    levels = {
    0:  "التحضيري :",
    1:  "الأولى :",
    2:  "الثانية :",
    3:  "الثالثة :",
    4:  "الرابعة :",
    5:  "الخامسة :",
    6:  "السادسة :"
    }   

    class_level = None

    for level,level_in_arab in levels.items():
        if class_name.startswith(level_in_arab) :
            class_level = level
            excess =len(level_in_arab)
            class_name= class_name[excess:]
            if (len(class_name))>0 and class_name[0] ==' ':
                class_name=class_name[1:]
            break
    
    if class_level == None:
            msg = 'l class hedha :"'+str(class_name) + '" meyebdech kima l patterns hedhom ???'+str(levels)
            msg+='\n t7b t3addih w say fck it sinn press "break" : '
            response = input(msg)
            if response=="break": 
                raise CustomError(msg)
    return (class_name,class_level)




def get_nbr_classes_and_elvs(ecole_slang:str,request:requests.session):
    r""" te5ou nbr classes w eleves mil mo3tayet l 3ama 
        mil site t3 l madrsa 
    """
    response = request.get(ecole_slang+"/info.php")

    pattern = re.compile(
        r"document.getElementById\('nbrclasse'\)\.innerHTML = '<strong>(.*?)</strong>'")

    match = re.search(pattern, response.text)
    nbr_class = match.group(1)

    pattern = re.compile(
        r"document.getElementById\('nbreleve'\)\.innerHTML = '<strong>(.*?)</strong>'")

    match = re.search(pattern, response.text)
    nbr_elvs = match.group(1)

    return (int(nbr_class),int(nbr_elvs))




def verifu_uid(eleve_uid:str):
    r"""return uid as it is if it s good if not get the min id +1 (under100k) to give it to an elv with no id """

    pattern = r'^\d{12}$'
    pattern2 = r'^\d{11}$'
    if re.search(pattern, eleve_uid) or re.search(pattern2, eleve_uid):
        return eleve_uid
    
    print("\n !!-found an elv with bad uid : '"+eleve_uid+"'\n")
    least_id = ElvsTunis.objects.filter(uid__lt=100000).aggregate(largest_uid=Max('uid'))['largest_uid']
    least_id+= nbr_elv_with_no_uid["nbr"] 
    nbr_elv_with_no_uid["nbr"]+=1
    return least_id




def get_elvs_de_classe(ecole_slang, classe_cid,request,ecole_id,classe_id):
    r""" ye5ou l id t3 l class w ymchi l url t3 pdf/final w ye5ou l tlemdha l kol wel uid te3hom
    """
     
    
    url = ecole_slang+"/pdf/pdf_recapfinal.php?id=" + \
        str(classe_cid)
    soup =send_get_request(url=url,request=request,decode=False)
    
    table_eleve = soup.find('table', {'border': '1', 'dir': 'rtl'})
    if not table_eleve:
        return []
    
    tds = [i for i in table_eleve.children if i != '\n'][1:]    # tlemdha kolhom ijiw f tds m3a b3dhhom mouch f tr w awil index houwa l tr t3 titles (ik)

    eleves=[]
    chunk_size = 8
    for i in range(0, len(tds), chunk_size):

        eleve_nom = tds[i].text.strip()
        eleve_uid = tds[i+1].text.strip()
        eleve_uid= verifu_uid(eleve_uid)

        eleve = ElvsTunis(
            uid=eleve_uid,
            nom_prenom=get_clean_name(eleve_nom),
            dirty_name= eleve_nom,
            ecole_id=ecole_id,
            classe_id=classe_id)

        eleves.append(eleve)
    return eleves




def bulkcreate_Classes_of_1ecole(ecole:EcolesTunis,request,nbr_class):
    print('\n-- extracting classes info --')
    url = ecole.slug + "/carnetnote.php"
    soup = send_get_request(url=url, request=request, decode=True)
    select_elment = soup.find('select', {'id': 'saisie_classe'})
    options = select_elment.find_all('option', {'id': 'select1'})
    
    classes_instances = []
    
    for option in options:
        class_cid = option['value']
        class_id = str(ecole.sid) +str(class_cid)
        class_name:str = option.text.strip()
        (class_name,class_level)=get_class_name_and_level(class_name)
    
        classe = ClassTunis(
            id =class_id,
            cid =class_cid ,
            class_name = class_name,
            level =class_level ,
            ecole_id = ecole.sid,
        )
        classes_instances.append(classe)
      
    url = ecole.slug + "/info.php"
    Verify_number_of_classes_matches(len(classes_instances),nbr_class)
    
    with transaction.atomic():
        ClassTunis.objects.bulk_create(
            classes_instances, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=[ "class_name", "level", "ecole_id"])
    



def bulkcreate_Eleves_of_1ecole(ecole:EcolesTunis,request,nbr_elvs):
    print('\n-- beginning extracting elvs --')
    classes = ClassTunis.objects.filter(ecole_id=ecole.sid)
    all_elvs_ecole = []

    nbr_elv_with_no_uid["nbr"]=1
    for index,classe in enumerate(classes) :
        print("traitment of classe ",str(index+1),"/",str(len(classes)))

        elvs_class =get_elvs_de_classe(ecole_slang=ecole.slug,classe_cid=classe.cid,request=request,ecole_id=ecole.sid,classe_id=classe.id)

        all_elvs_ecole.extend(elvs_class)
        time.sleep(1)

    
    Verify_number_of_elvs_matches(nbr_eleves_instances=len(all_elvs_ecole),nbr_eleves=nbr_elvs)
    with transaction.atomic():            
        ElvsTunis.objects.bulk_create(
            all_elvs_ecole, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=[ "nom_prenom", "dirty_name", "ecole_id","classe_id"])
        print("\nlen eleves = ",str(len(all_elvs_ecole)))