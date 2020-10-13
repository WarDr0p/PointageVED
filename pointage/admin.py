from django.contrib import admin
from .models import User,Entree,PrevEntree,Asso

admin.site.register(Entree)
admin.site.register(PrevEntree)
admin.site.register(Asso)
