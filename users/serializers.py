from rest_framework import serializers
from django.contrib.auth.models import User

from x.models import Dre


class UserSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = User
        fields =['id','username','password','email']