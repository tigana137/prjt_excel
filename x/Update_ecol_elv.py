import re
import time
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from bidict import bidict

from django.db import IntegrityError, transaction
from requests.exceptions import ChunkedEncodingError
from rest_framework.response import Response
from x.functions import check_if_sid_need_to_be_replaced, get_clean_name, get_clean_name_for_school_name, get_dre_id_from_select_element, get_url_return_soup, post_url_return_soup


from x.models import AdminEcoledata, AdminElvs, Del1,  Dre, Elvsprep
from pprint import pprint

# [l ids l yelzmhom ytbadlou] : actual id fil db
sids_to_replace = bidict({"842911": "842811",
                          "842913": "842813",
                          "842922": "842822",
                          "842923": "842823",
                          "842924": "842824",
                          "842912": "842812",
                          "842914": "842814"
                          })




# bulkcreate l data t3 mders f admin ecole data prive w etatik
def create_AdminEcole_data(request2: requests.Session):

    ############# etatiq #############

    soup = get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/index.php?op=inscprim&act=find_etab", request=request2,decode=True)

    dre = get_dre_id_from_select_element(soup)

    existing_sids_in_db = set(AdminEcoledata.objects.filter(
        dre_id=dre).values_list('sid', flat=True))

    soup = get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/inscprim/getetab_choix.php?id="+dre, request=request2,decode=True)

    options = soup.find_all('option')

    admin_ecoles_array = []
    new_ecoles_to_add_their_Levelstat = []

    for option in options:
        sid = option['value']
        sid = check_if_sid_need_to_be_replaced(sid, etatiq=True)

        school_name = option.get_text()
        school_name = get_clean_name_for_school_name(
            school_name, etatique=True)

        ecole = AdminEcoledata(
            sid=sid,
            school_name=school_name,
            dre_id=dre,
            del1_id=sid[:4],
        )

        if int(sid) not in existing_sids_in_db:  # create Levelstat instances for the levels
            print('New ecole !! :  ' + school_name + sid)
            new_ecoles_to_add_their_Levelstat.append(ecole)

        admin_ecoles_array.append(ecole)

    ############# privee #############

    soup = get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/prive/getetab_prive_prim.php?id="+dre, request=request2,decode=True)

    options = soup.find_all('option')

    for option in options:

        sid = option['value']
        sid = check_if_sid_need_to_be_replaced(sid, prive=True)

        school_name = option.get_text()
        school_name = get_clean_name_for_school_name(school_name, prive=True)

        ecole = AdminEcoledata(
            sid=sid,
            school_name=school_name,
            dre_id=dre,
            del1_id=sid[:4],
        )
        admin_ecoles_array.append(ecole)

    with transaction.atomic():
        AdminEcoledata.objects.bulk_create(
            admin_ecoles_array, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=["school_name"])
        for ecole in new_ecoles_to_add_their_Levelstat:
            ecole.create_levelstats()
        print("updating AdminEcoledata done succesfully")

    return Response(True)


# ~ zid comparision bin l sids l 5dhithom welli 3ndk famch zeyed walla ne9s
# ~ les preivees in all dre 3ndhom **98 del ?
# bulkcreate lil AdminElvs2 l request 5dheha mil Verify capatcha 5atr lezmn bypass heki bch tod5al donc torbtha m3aha in case of ist3mel
def create_AdminElvs(request2: requests.Session):

    def is_valid_date_string(date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # privee
    sids = AdminEcoledata.objects.filter(
        del1_id=8498).values_list('sid', flat=True)

    for sid in sids:
        elvs_array = []
        url = "https://suivisms.cnte.tn/ministere/index.php?op=prive&act=list_eleve_prive_prim"
        payload = {
            "code_dre": "84",
            "code_etab": sid,
            "btenv": "بحث"
        }
        response = request2.post(url=url, data=payload)

        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')

        rows = soup.find_all('tr', {'height': '30', 'bgcolor': '#B9FFB9'})

        # print(rows[0].find_all('td', {'align': 'center'}))

        for tr in rows:
            data = tr.findAll('font')
          #  temp_uid = data[1].text.strip()
            uid = data[2].text.strip()
            if uid == "" or uid == "0" or not uid.isdigit():
                print('fama uid egal 0 wall "" :', end='')
                print(uid)
                continue
            nom_prenom = data[3].text.strip()
            nom_pere = data[4].text.strip()
            date_naissance = data[5].text.strip()
            elv = AdminElvs(
                uid=uid,
                nom_prenom=get_clean_name(nom_prenom),
                nom_pere=get_clean_name(nom_pere),
                date_naissance=date_naissance if is_valid_date_string(
                    date_naissance) else None,
                ecole_id=sid,
                #   temp_uid=temp_uid
            )
            elvs_array.append(elv)

        try:
            AdminElvs.objects.bulk_create(elvs_array, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=[
                                          "nom_prenom", "nom_pere", "date_naissance", "ecole_id"])
            print(str(sid)+' : good ' + str(len(elvs_array)) + ' elvs')

        except IntegrityError as e:
            print("------------")
            print("errerur with this : " + str(sid))
            print(f"IntegrityError: {e}")
            print("------------")

    # etatik

    response = request2.get(
        "https://suivisms.cnte.tn/ministere/index.php?op=inscprim&act=find_etab")
    soup = bs(response.content.decode(
        encoding='utf-8', errors='ignore'), 'html.parser')
    dre_select_elm = soup.find('select', {'name': 'code_dre'})

    options = dre_select_elm.findAll('option')
    dre = '84'  # ~
    existing_sids = set(AdminEcoledata.objects.filter(
        dre_id=dre).values_list('sid', flat=True))
    if len(options) == 2:  # ~ lezmhm nrmlmnt l kol zouz loula kil ---- w b3d l weileya chouf ken le nik errur or somethn
        dre = options[1]['value']
    response = request2.get(
        "https://suivisms.cnte.tn/ministere/inscprim/getetab_choix.php?id="+dre)
    select_element = response.content.decode(encoding='utf-8', errors='ignore')
    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_element)

    for sid in sids:
        print("currently traiment of : " + str(sid))
        elvs_array = []
        url = "https://suivisms.cnte.tn/ministere/index.php?op=inscprim&act=list_eleve"
        payload = {
            "code_dre": "84",
            "code_etab": sid,
            "btenv": "بحث"
        }

        response = request2.post(url=url, data=payload)

        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')

        rows = soup.find_all('tr', {'height': '30', 'bgcolor': '#a9edca'})

        for tr in rows:
            data = tr.findAll('font')

            uid = data[1].text.strip()
            if uid == "" or uid == "0" or not uid.isdigit():
                continue
            nom_prenom = data[2].text.strip()
            nom_pere = data[3].text.strip()
            date_naissance = data[4].text.strip()
            elv = AdminElvs(
                uid=uid,
                nom_prenom=get_clean_name(nom_prenom),
                nom_pere=get_clean_name(nom_pere),
                date_naissance=date_naissance if is_valid_date_string(
                    date_naissance) else None,
                ecole_id=int(sid) if str(
                    sid) not in sids_to_replace.keys() else sids_to_replace[sid]
            )
            elvs_array.append(elv)

        try:
            AdminElvs.objects.bulk_create(elvs_array, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=[
                                          "nom_prenom", "nom_pere", "date_naissance", "ecole_id"])
            print(str(sid)+' : good ' + str(len(elvs_array)) + ' elvs')

        except Exception as e:
            print("------------")
            print("erreur with this : " + str(sid))
            print(f"Exception : {e}")
            print("------------")

    return Response(True)


def create_Elvsprep(request2: requests.Session):
    # request2.get(
    #     "https://suivisms.cnte.tn/ministere/index.php?op=preparatoire&act=inscrit_find")
    # response = request2.get(
    #     "https://suivisms.cnte.tn/ministere/preparatoire/getetabprint.php?id=84")
    soup = get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/index.php?op=preparatoire&act=inscrit_find", request=request2,decode=True)

    dre = get_dre_id_from_select_element(soup)

    select_element =str( get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/preparatoire/getetabprint.php?id="+dre, request=request2,decode=True))

    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_element)
    if sids[0] == '0':
        del sids[0]

    for sid in sids:
        elvs_array = []
        url = "https://suivisms.cnte.tn/ministere/preparatoire/liste_inscrit.php"
        payload = {
            "code_dre": "84",
            "code_etab": sid,
            "btenv": "طباعة"
        }
        
        soup = post_url_return_soup(url=url,payload=payload,request=request2,decode=True)

        table = soup.find('table', {'id': 'datatables', }).tbody
        tr_s = [i for i in table.children if i != '\n']

        for tr in tr_s:
            tds = [i for i in tr.children if i != '\n']
            uid = tds[1].text.strip()

            nom = tds[2].text.strip()
            nom = get_clean_name(nom)

            prenom = tds[3].text.strip()
            prenom= get_clean_name(prenom)

            date_naissance = tds[4].text.strip()

            sid = check_if_sid_need_to_be_replaced(sid, etatiq=True)

            eleve = Elvsprep(
                uid=uid,
                nom=nom,
                prenom=prenom,
                date_naissance=date_naissance,
                ecole_id=sid ,
            )
            elvs_array.append(eleve)

        with transaction.atomic():
            Elvsprep.objects.bulk_create(elvs_array, ignore_conflicts=False, update_conflicts=True, update_fields=[
                                         "nom", "prenom", "date_naissance", "ecole_id"])
            print(str(sid)+' : good ' + str(len(elvs_array)) + ' elvs')


    return Response(True)


def create_Elvpremiere(request2: requests.Session):
    request2.get(
        "https://suivisms.cnte.tn/ministere/index.php?op=primaire&act=inscrit_find")
    response = request2.get(
        "https://suivisms.cnte.tn/ministere/primaire/getetabprint1.php?id=84")

    select_element = response.content.decode(encoding='utf-8', errors='ignore')
    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_element)
    if sids[0] == '0':
        del sids[0]
    for sid in sids:
        elvs_array = []
        url = "https://suivisms.cnte.tn/ministere/primaire/liste_inscrit.php"
        payload = {
            "code_dre": "84",
            "code_etab": sid,
            "btenv": "طباعة"
        }

        response = request2.post(url=url, data=payload)

        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')

        table = soup.find('table', {'id': 'datatables', }).tbody

        tr_s = [i for i in table.children if i != '\n']

        for tr in tr_s:
            tds = [i for i in tr.children if i != '\n']
            uid = tds[1].text.strip()
            nom_prenom = tds[2].text.strip() + " " + tds[3].text.strip()
            date_naissance = tds[4].text.strip()
            eleve = AdminElvs(
                uid=uid,
                nom_prenom=get_clean_name(nom_prenom),
                date_naissance=date_naissance,
                ecole_id=sid if str(sid) not in sids_to_replace.keys(
                ) else sids_to_replace[str(sid)],
            )
            elvs_array.append(eleve)

        try:
            AdminElvs.objects.bulk_create(elvs_array, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=[
                                          "nom_prenom", "date_naissance", "ecole_id"])
            print(str(sid)+' : good ' + str(len(elvs_array)) + ' elvs')

        except IntegrityError as e:
            print("------------")
            print("errerur with this : " + str(sid))
            print(f"IntegrityError: {e}")
            print("------------")

    return Response(True)
