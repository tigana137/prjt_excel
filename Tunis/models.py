from django.db import models


class DreTunis(models.Model):    # wileya
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    dre_id_in_cnte = models.PositiveSmallIntegerField(null=True)


class EcolesTunis(models.Model):
    sid = models.IntegerField(primary_key=True)
    school_name = models.CharField(max_length=100)
    principal = models.CharField(max_length=100, blank=True, null=True)
    dre = models.ForeignKey(
        DreTunis, on_delete=models.SET_NULL, blank=True, null=True, related_name="ecoles")
    slug = models.CharField(max_length=200, null=True)

    extracted_from = models.BooleanField(default=False)


class ClassTunis(models.Model):
    id = models.IntegerField(primary_key=True)
    cid = models.IntegerField()
    class_name = models.CharField(max_length=100)
    level = models.IntegerField(choices=[(i, str(i)) for i in range(7)])
    ecole = models.ForeignKey(
        EcolesTunis, on_delete=models.SET_NULL, blank=True, null=True, related_name="classes")

    class Meta:
        unique_together = ('cid', 'ecole')


class ElvsTunis(models.Model):
    uid = models.BigIntegerField(primary_key=True)
    nom_prenom = models.CharField(max_length=200)
    dirty_name = models.CharField(max_length=200)
    ecole = models.ForeignKey(
        EcolesTunis, on_delete=models.SET_NULL, blank=True, null=True)
    classe = models.ForeignKey(
        ClassTunis, on_delete=models.SET_NULL, blank=True, null=True)


class ElvsTunis11(models.Model):
    uid = models.BigAutoField(primary_key=True)
    nom_prenom = models.CharField(max_length=200)
    dirty_name = models.CharField(max_length=200)
    ecole = models.ForeignKey(
        EcolesTunis, on_delete=models.SET_NULL, blank=True, null=True)
    classe = models.ForeignKey(
        ClassTunis, on_delete=models.SET_NULL, blank=True, null=True)
