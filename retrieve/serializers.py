from rest_framework import serializers

from x.models import AdminElvs




class AdminEcoledataSerializer(serializers.ModelSerializer):
    # premiere = levelstatSerializer()
    # deuxieme = levelstatSerializer()
    # troisieme = levelstatSerializer()
    # quatrieme = levelstatSerializer()
    # cinquieme = levelstatSerializer()
    # sixieme = levelstatSerializer()

    class Meta(object):
        model = AdminElvs
        fields = ["sid", "school_name", "principal"]

