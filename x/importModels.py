

from datetime import datetime
from decimal import Decimal
import json
from x.models import AdminEcoledata, AdminElvs, Del1, Dre, Elvsprep, levelstat
from datetime import date

path = ""
path = "prjt_excel/"  # add this only for the pythonanywhere


def importDre():
    with open(path+'DB/Dre.json', 'r') as json_file:
        data = json.load(json_file)

    model_instances = []
    for item in data:
        # Create model instance using item
        instance = Dre(**item)
        model_instances.append(instance)

    Dre.objects.bulk_create(model_instances, ignore_conflicts=False,
                            update_conflicts=True, update_fields=["username", "password"])
    return


def importDel1():
    with open(path+'DB/Del1.json', 'r') as json_file:
        data = json.load(json_file)

    model_instances = []
    for item in data:
        # Create model instance using item
        instance = Del1(**item)
        model_instances.append(instance)

    Del1.objects.bulk_create(model_instances, ignore_conflicts=False,update_conflicts=True, update_fields=["name"])
    return


def importlevelstat():
    with open(path+'DB/levelstat.json', 'r') as json_file:
        data = json.load(json_file)

    model_instances = []
    for item in data:
        # Create model instance using item
        item["nbr_classes"] = Decimal(item['nbr_classes'])
        instance = levelstat(**item)
        model_instances.append(instance)

    levelstat.objects.bulk_create(
        model_instances, ignore_conflicts=False, update_conflicts=True, update_fields=["nbr_elvs", "nbr_classes", "nbr_leaving", "nbr_comming"])
    return


def importAdminEcoledata():
    with open(path+'DB/AdminEcoledata.json', 'r') as json_file:
        data = json.load(json_file)

    model_instances = []
    for item in data:
        # Create model instance using item
        instance = AdminEcoledata(**item)
        model_instances.append(instance)

    AdminEcoledata.objects.bulk_create(
        model_instances, ignore_conflicts=False, update_conflicts=True, update_fields=["school_name", "ministre_school_name","principal",])
    return


def convert_date_naissance_totype_Date(date):
    return datetime.strptime(date, '%Y-%m-%d').date()
def importAdminElvs():
    with open(path+'DB/AdminElvs.json', 'r') as json_file:
        data = json.load(json_file)

    model_instances = []
    for item in data:
        # Create model instance using item
        item["date_naissance"] = convert_date_naissance_totype_Date(item["date_naissance"])
        instance = AdminElvs(**item)
        model_instances.append(instance)

    AdminElvs.objects.bulk_create(
        model_instances, batch_size=1000, ignore_conflicts=False, update_conflicts=True, update_fields=["nom_prenom", "nom_pere", "date_naissance","ecole_id"])
    return


def importElvsprep():
    with open(path+'DB/Elvsprep.json', 'r') as json_file:
        data = json.load(json_file)

    model_instances = []
    for item in data:
        # Create model instance using item
        item["date_naissance"] = convert_date_naissance_totype_Date(item["date_naissance"])
        instance = Elvsprep(**item)
        model_instances.append(instance)

    Elvsprep.objects.bulk_create(
        model_instances, batch_size=1000, ignore_conflicts=False, update_conflicts=True, update_fields=["nom", "prenom", "date_naissance","ecole_id"])
    return
