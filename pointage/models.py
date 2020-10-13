from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

SALLE_CHOICES = [
    ('A', 'Atelier'),
    ('B', "Bureau d'étude"),
    ('D', 'Découpe laser')
]


class Entree(models.Model):
    entree = models.DateTimeField()
    sortie = models.DateTimeField(null=True)
    User = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 verbose_name="passage")
    salle = models.CharField(
        max_length=1,
        choices=SALLE_CHOICES,
        default="B",
    )

    def __str__(self):
        return self.User.__str__()+" à "+self.get_salle_display()+" de "+str(self.entree)[0:16]+" à "+(str(self.sortie)[0:16] if self.sortie != None else str('encore présent(e)'))

class PrevEntree(models.Model):
    entree = models.DateTimeField()
    sortie = models.DateTimeField(null=True)
    User = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 verbose_name="prevpassage")
    salle = models.CharField(
        max_length=1,
        choices=SALLE_CHOICES,
        default="B",
    )

    def __str__(self):
        return self.User.__str__()+" à "+self.get_salle_display()+" de "+str(self.entree)[0:16]+" à "+(str(self.sortie)[0:16] if self.sortie != None else str('encore présent(e)'))
ASSO_CHOICES = [
    ('danger', 'danger'),
    ('info', "info"),
    ('success', 'success'),
    ('alert', 'alert')
]
class Asso(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    color=models.CharField(
        max_length=8,
        choices=ASSO_CHOICES,
        default="danger",
    )
    def __str__(self):
        return self.user.first_name+" "+self.user.last_name+" "+self.color

