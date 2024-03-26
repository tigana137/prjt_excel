

import json
import requests
from django.core.exceptions import ObjectDoesNotExist

from x.models import AdminEcoledata
from .Update_ecol_elv import sids_to_replace


def verify_sid(sid):
    if str(sid) not in sids_to_replace.keys():
        return sid
    return sids_to_replace[str(sid)]


def update_principals_in_dre(request: requests.Session, gov_id: int, start: int,):
    url = "http://www.ent1.cnte.tn/ent/liste_ecole/affiche_ecole.php?"
    url_with_params = url+"&gov=" +  str(gov_id) + "&start=" + str(start) + "&length=100"
    response = request.get(url_with_params)
    content = response.content.decode('utf-8-sig')
    data = json.loads(content)
    ecole_data = data["data"]
    principals_data = []
    for ecole in ecole_data:
        sid = ecole[1]
        sid = verify_sid(sid)
        principal_name = ecole[3]
        school_name = ecole[2]  # just to print it out in the exception in case it doesnt exist
        ecole = AdminEcoledata(sid=sid, principal=principal_name,school_name=school_name)
        principals_data.append(ecole)
    
    AdminEcoledata.objects.bulk_update(principals_data, fields=["principal"])

    total_ecoles_number = data["recordsTotal"]
    if int(total_ecoles_number) > start+100:
        update_principals_in_dre(request,gov_id,start=start+100)
    


def update_principals():
    request = requests.session()
    goverments = {  # l ids t3 kol dre fil site ent3 (rabi ynoub b akthr)
        "sousse": 7
    }

    for gov_name, gov_id in goverments.items():
        print("currently update_principals of "+gov_name)
        update_principals_in_dre(request, gov_id, start=0)
        print("traitment ended succefully of "+gov_name ,end="\n ------- \n -------- \n")

    return
