import json
from x.models import AdminEcoledata, AdminElvs, Del1, Dre, Elvsprep, levelstat
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date


def exportDre():
    data = Dre.objects.all().values()
    data_list = list(data)
    with open("DB/Dre.json", 'w') as json_file:
        json.dump(data_list, json_file, indent=2)


def exportDel1():
    data = Del1.objects.all().values()
    data_list = list(data)
    with open("DB/Del1.json", 'w') as json_file:
        json.dump(data_list, json_file, indent=2)


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)  # Convert Decimal to string
        return super().default(obj)
def exportlevelstat():
    data = levelstat.objects.all().values()
    data_list = list(data)
    with open("DB/levelstat.json", 'w') as json_file:
        json.dump(data_list, json_file,cls=CustomJSONEncoder, indent=2)


def exportAdminEcoledata():
    data = AdminEcoledata.objects.all().values()
    data_list = list(data)
    with open("DB/AdminEcoledata.json", 'w') as json_file:
        json.dump(data_list, json_file, indent=2)


class DateAwareJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return str(obj)
        return super().default(obj)
    
def exportAdminElvs():
    data = AdminElvs.objects.all().values()
    data_list = list(data)
    with open("DB/AdminElvs.json", 'w') as json_file:
        json.dump(data_list, json_file,cls=DateAwareJSONEncoder, indent=2)


def exportElvsprep():
    data = Elvsprep.objects.all().values()
    data_list = list(data)
    with open("DB/Elvsprep.json", 'w') as json_file:
        json.dump(data_list, json_file,cls=DateAwareJSONEncoder, indent=2)

