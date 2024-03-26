

from rest_framework import serializers
from x.models import AdminEcoledata, levelstat


class levelstatSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = levelstat
        fields = ["nbr_elvs", "nbr_classes", "nbr_leaving", "nbr_comming"]


class AdminEcoledataSerializer(serializers.ModelSerializer):
    # premiere = levelstatSerializer()
    # deuxieme = levelstatSerializer()
    # troisieme = levelstatSerializer()
    # quatrieme = levelstatSerializer()
    # cinquieme = levelstatSerializer()
    # sixieme = levelstatSerializer()

    class Meta(object):
        model = AdminEcoledata
        fields = ["sid", "ministre_school_name", "principal"]

