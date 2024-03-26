from django.db import models

# Create your models here.


class Dre(models.Model):    # wileya
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)


class Del1(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    dre = models.ForeignKey(
        Dre, on_delete=models.SET_NULL, blank=True, null=True,related_name='Del1s')


class levelstat(models.Model):
    lid = models.IntegerField(primary_key=True)
    nbr_elvs = models.PositiveSmallIntegerField(default=0)
    nbr_classes = models.DecimalField(
        max_digits=3,  # 20 + 2 (for digits before and after the decimal point)
        decimal_places=1,  # Adjust based on your requirements
        default=0
    )
    nbr_leaving = models.PositiveSmallIntegerField(default=0)
    nbr_comming = models.PositiveSmallIntegerField(default=0)

    def current_elv_number(self):
        return  self.nbr_elvs+self.nbr_comming - self.nbr_leaving
    
    def kethefa_after_comming(self):
        return (self.current_elv_number()+1)/self.nbr_classes

    def kethefa_after_leaving(self):
        return (self.current_elv_number()-1)/self.nbr_classes

    @property
    def get_sid(self):
        """
        Get the first four digits of lid.
        """
        lid_str = str(self.lid)
        return lid_str[:6]

    def add_elv(self):
        self.nbr_comming += 1
        self.save()

    def cancel_add_elv(self):
        self.nbr_comming -= 1
        self.save()

    def reduce_elv(self):
        self.nbr_leaving += 1
        self.save()

    def cancel_reduce_elv(self):
        self.nbr_leaving -= 1
        self.save()


class AdminEcoledata(models.Model):
    sid = models.IntegerField(primary_key=True)
    school_name = models.CharField(max_length=100)
    ministre_school_name = models.CharField(max_length=100, blank=True)
    principal = models.CharField(max_length=100, blank=True, null=True)
    dre = models.ForeignKey(
        Dre, on_delete=models.SET_NULL, blank=True, null=True)
    del1 = models.ForeignKey(
        Del1, on_delete=models.SET_NULL, blank=True, null=True, related_name="ecoles")

    premiere = models.ForeignKey(
        levelstat, on_delete=models.PROTECT, blank=True, null=True)

    deuxieme = models.ForeignKey(
        levelstat, on_delete=models.PROTECT, blank=True, null=True, related_name="deuxieme")
    troisieme = models.ForeignKey(
        levelstat, on_delete=models.PROTECT, blank=True, null=True, related_name="troisieme")
    quatrieme = models.ForeignKey(
        levelstat, on_delete=models.PROTECT, blank=True, null=True, related_name="quatrieme")
    cinquieme = models.ForeignKey(
        levelstat, on_delete=models.PROTECT, blank=True, null=True, related_name="cinquieme")
    sixieme = models.ForeignKey(
        levelstat, on_delete=models.PROTECT, blank=True, null=True, related_name="sixieme")

    stat = [premiere, deuxieme, troisieme]

    def create_levelstats(self):
        premiere_data = levelstat.objects.create(lid=str(self.sid)+'1')
        deuxieme_data = levelstat.objects.create(lid=str(self.sid)+'2')
        troisieme_data = levelstat.objects.create(lid=str(self.sid)+'3')
        quatrieme_data = levelstat.objects.create(lid=str(self.sid)+'4')
        cinquieme_data = levelstat.objects.create(lid=str(self.sid)+'5')
        sixieme_data = levelstat.objects.create(lid=str(self.sid)+'6')
        self.premiere = premiere_data
        self.deuxieme = deuxieme_data
        self.troisieme = troisieme_data
        self.quatrieme = quatrieme_data
        self.cinquieme = cinquieme_data
        self.sixieme = sixieme_data

    def initial_total_elvs(self):  # elvs f 30 out
        return self.premiere.nbr_elvs + self.deuxieme.nbr_elvs + self.troisieme.nbr_elvs + self.quatrieme.nbr_elvs + self.cinquieme.nbr_elvs + self.sixieme.nbr_elvs

    def nbr_all_leaving(self):  # 3ada l mou8adirin
        return self.premiere.nbr_leaving + self.deuxieme.nbr_leaving + self.troisieme.nbr_leaving + self.quatrieme.nbr_leaving + self.cinquieme.nbr_leaving + self.sixieme.nbr_leaving

    def nbr_all_comming(self):  # 3ada l jeying
        return self.premiere.nbr_comming + self.deuxieme.nbr_comming + self.troisieme.nbr_comming + self.quatrieme.nbr_comming + self.cinquieme.nbr_comming + self.sixieme.nbr_comming

    def get_total_nbr_elvs(self):
        return self.initial_total_elvs() + self.nbr_all_comming() - self.nbr_all_leaving()

    def get_total_nbr_classes(self):
        return self.premiere.nbr_classes + self.deuxieme.nbr_classes + self.troisieme.nbr_classes + self.quatrieme.nbr_classes + self.cinquieme.nbr_classes + self.sixieme.nbr_classes

    def nbr_comming_leaving(self):
        return self.nbr_all_comming() - self.nbr_all_leaving()

    def update_levelstat(self, premier, deuxieme, troisieme, quaterieme, cinqieme, sixieme: tuple):
        self.premiere.nbr_elvs, self.premiere.nbr_classes = premier
        self.deuxieme.nbr_elvs, self.deuxieme.nbr_classes = deuxieme
        self.troisieme.nbr_elvs, self.troisieme.nbr_classes = troisieme
        self.quatrieme.nbr_elvs, self.quatrieme.nbr_classes = quaterieme
        self.cinquieme.nbr_elvs, self.cinquieme.nbr_classes = cinqieme
        self.sixieme.nbr_elvs, self.sixieme.nbr_classes = sixieme
        self.premiere.save()
        self.deuxieme.save()
        self.troisieme.save()
        self.quatrieme.save()
        self.cinquieme.save()
        self.sixieme.save()

    # def delete(self, using: Any = ..., keep_parents: bool = ...) -> tuple[int, dict[str, int]]:    ~ lezmk ki tfach5 madrsa tfas5 m3aha l levstat
    #    levelstat.objects.filter(lid__statswith=str(self.sid)).delete()
    #    return super().delete(using, keep_parents)


class AdminElvs(models.Model):
    uid = models.BigIntegerField(primary_key=True)
    nom_prenom = models.CharField(max_length=200)
    nom_pere = models.CharField(max_length=200)
    date_naissance = models.DateField(null=True, blank=True)
    ecole = models.ForeignKey(
        AdminEcoledata, on_delete=models.CASCADE, blank=True, null=True)


class Elvsprep(models.Model):
    uid = models.BigIntegerField(primary_key=True)
    nom = models.CharField(max_length=200)
    prenom = models.CharField(max_length=200)
    date_naissance = models.DateField(null=True, blank=True)
    ecole = models.ForeignKey(
        AdminEcoledata, on_delete=models.CASCADE, blank=True, null=True)



class Tuniselvs(models.Model):
    uid = models.BigIntegerField(null=True, blank=True)
    nom_prenom = models.CharField(max_length=200,null=True, blank=True)
    classe_id =models.CharField(max_length=200,null=True, blank=True)
    ecole_name = models.CharField(max_length=200)
    ecole_id = models.IntegerField()


class DirtyNames(models.Model):
    uid = models.BigIntegerField(null=True, blank=True)
    nom_prenom = models.CharField(max_length=200,null=True, blank=True)
    classe_id =models.CharField(max_length=200,null=True, blank=True)
    ecole_name = models.CharField(max_length=200)
    ecole_id = models.IntegerField()