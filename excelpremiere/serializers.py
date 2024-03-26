from rest_framework import serializers

from excel.models import excelsheets


class excelsheetsSerializerPremiere(serializers.ModelSerializer):

    class Meta(object):
        model = excelsheets
        fields =["uid","nom","prenom","date_naissance","prev_ecole","prev_ecole_id","Del1","next_ecole","next_ecole_id","reason","decision","comments","dre_id"]