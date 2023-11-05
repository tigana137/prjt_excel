from django.db import models

# Create your models here.


class Dre(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class Del1(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class AdminEcoledata2(models.Model):
    sid = models.IntegerField(primary_key=True)
    school_name = models.CharField(max_length=100)
    dre = models.ForeignKey(
        Dre, on_delete=models.SET_NULL, blank=True, null=True)
    del1 = models.ForeignKey(
        Del1, on_delete=models.SET_NULL, blank=True, null=True)
    

class AdminElvs(models.Model):
    uid = models.BigIntegerField(primary_key=True)
    nom_prenom = models.CharField(max_length=200)
    nom_pere = models.CharField(max_length=200)
    date_naissance = models.DateField(null=True, blank=True)
    ecole = models.ForeignKey(AdminEcoledata2, on_delete=models.PROTECT)