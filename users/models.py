from django.db import models
from django.contrib.auth.models import User

from x.models import Dre



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add other fields as needed for your UserProfile model
    dre = models.ForeignKey(
        Dre, on_delete=models.SET_NULL, blank=True, null=True)

    
    def __str__(self):
        return self.user.username
    



