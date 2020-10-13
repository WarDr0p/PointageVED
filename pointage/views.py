from django.contrib.auth import authenticate
from django.shortcuts import render
from .models import Entree, PrevEntree,Asso
from django.http import Http404
from django.shortcuts import redirect
import numpy as np
from pointage.forms import SignIn, Add, ReserveForm, ChooseRoom, ChangePasswordForm
from django.contrib.auth import authenticate, logout as dj_logout, login as dj_login
from django.contrib.auth.models import User
import pandas as pd
import plotly.express as px
import plotly.io as pio
from plotly.offline import plot
from django.utils import timezone
import plotly.graph_objects as go
import pytz


import datetime
_LIMIT_BE = 10
_LIMITE_A = 10
_LIMITE_DL = 5

def redirectindex(request):
    return redirect("index")
# Create your views here.
def entry(request, person_id):
    if request.user.is_authenticated:
        try:
            personne = User.objects.get(pk=person_id)
            listePersIn, listePersOut,entreeE = getInOut()
            if request.user.id == person_id or request.user.is_staff:
                if personne in listePersOut:
                    if request.method == 'POST':
                        form = ChooseRoom(request.POST)
                        if form.is_valid():
                            entree = Entree(entree=timezone.datetime.now().replace(tzinfo=pytz.utc), sortie=None, User=personne,salle=form.cleaned_data.get("salle"))
                            entree.save()
                            entreeE.append(entree)
                            listePersIn.append(personne)
                            listePersOut.remove(personne)
                            return render(request, 'pointage/presencebis.html',
                                      {"In": entreeE, "Out": listePersOut, 'success': personne.first_name +" "+personne.last_name+" est rentré(e) à "+entree.get_salle_display()+" le "+ str(timezone.datetime.now().date())+" à "+str(timezone.datetime.now().time().isoformat())[0:5]})
                        return render(request, 'pointage/presencebis.html',
                                      {"In": entreeE, "Out": listePersOut,
                                       'error': "Erreur dans le choix de la salle"})
                    return render(request, 'pointage/presencebisform.html',
                                      {"form":ChooseRoom()})
                return render(request, 'pointage/presencebis.html',
                              {"In": entreeE, "Out": listePersOut,
                               'error': personne.first_name +" "+personne.last_name+" est déja dans la salle"})
            return render(request, 'pointage/presencebis.html',
                          {"In": entreeE, "Out": listePersOut,
                           'error': "Vous ne pouvez pas intéragir avec les actions de quelqun d'autre"})

        except User.DoesNotExist:
            listePersIn, listePersOut = getInOut()
            return render(request, 'pointage/presencebis.html', {"In": listePersIn, "Out": listePersOut,'error':"la personne sélectionnée n'existe pas"})
    else:
        return redirect(request,"index")
def exit(request, person_id):
    if request.user.is_authenticated:
        try:
            personne = User.objects.get(pk=person_id)
            listePersIn, listePersOut,entreeE = getInOut()
            if request.user.id == person_id or request.user.is_staff:
                if personne in listePersIn:
                    for entree in Entree.objects.filter(User=personne):
                        if entree.sortie == None:
                            entreeE.remove(entree)
                            entree.sortie = timezone.datetime.now().replace(tzinfo=pytz.utc)
                            entree.save()
                    listePersOut.append(personne)
                    listePersIn.remove(personne)
                    return render(request, 'pointage/presencebis.html',
                              {"In": entreeE, "Out": listePersOut, 'success': personne.first_name +" "+personne.last_name+" est parti(e) de "+entree.get_salle_display()+" le "+ str(timezone.datetime.now().date())+" à "+str(timezone.datetime.now().time().isoformat())[0:5]})
                return render(request, 'pointage/presencebis.html',
                              {"In": entreeE, "Out": listePersOut,
                               'error': personne.first_name +" "+personne.last_name+" est déja hors de la salle"})
            return render(request, 'pointage/presencebis.html',
                          {"In": entreeE, "Out": listePersOut,
                           'error': "Vous ne pouvez pas intéragir avec les action de quelqun d'autre"})

        except User.DoesNotExist:
            listePersIn, listePersOut,entree = getInOut()
            return render(request, 'pointage/presencebis.html', {"In": entree, "Out": listePersOut,'error':"la personne sélectionnée n'existe pas"})
    else:
        redirect(request,"index")
def index(request):
    if request.user.is_authenticated:
        listePersIn,listePersOut,entree = getInOut()
        return render(request, 'pointage/presence.html',{"In":entree, "Out":listePersOut})
    else:
        return render(request, 'pointage/index.html', {})

def getInOut():
    entrees = Entree.objects.all()
    entreeEnCours = []
    listePersIn = []
    for entree in entrees:
        if entree.sortie == None:
            listePersIn.append(entree.User)
            entreeEnCours.append(entree)
    listePersOut = list(set(User.objects.order_by('last_name', 'first_name')).difference(listePersIn))
    return listePersIn,sorted(listePersOut,key=lambda x:x.last_name + x.first_name),entreeEnCours

def account(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = SignIn(request.POST)
            if form.is_valid():
                user = authenticate(request, username=form.cleaned_data.get('pseudo'), password=form.cleaned_data.get('passw'));
                if user is not None:
                    dj_login(request, user)
                    return redirect("index")
                else:
                    form = SignIn()
                    return render(request, 'pointage/login.html', {"form": form, "error":"Erreur dans le couple identifiant mot de passe"})
        else:
            form = SignIn(),
            return render(request, 'pointage/login.html', {"form":form })
    else:
        resas = PrevEntree.objects.filter(User=request.user)
        if request.user.is_staff:
            return render(request, 'pointage/account.html', {"staff":"","pseudo":request.user.username,"resas":resas})
        else:
            return render(request,'pointage/account.html',{"resas":resas})

def logout(request):
    dj_logout(request)
    return redirect("index")

def add(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = Add(request.POST)
            if form.is_valid():
                personne = User(last_name=form.cleaned_data.get('nom'), first_name=form.cleaned_data.get('prenom'), asso=form.cleaned_data.get('asso'))
                personne.save()
                return redirect("index")
            else:
                return render(request, "pointage/add.html",{"form":form, "error":"Il semble que vous ayez mal rempli le formulaire"})
        else:
            form = Add()
            return render(request, "pointage/add.html",{"form":form})
    else:
        return redirect(request,"index")

def backindex(request, person_id):
    return redirect('index')

def backaccount(request, person_id):
    return redirect('../account')

def backprev(request, person_id):
    return redirect('../nextpassage')

def conta(request):
    personnes = User.objects.order_by('last_name', 'first_name')
    return render(request,"pointage/conta.html",{"personnes":personnes})

def containfo(request, person_id):
    if request.user.is_authenticated:
        try:
            personne = User.objects.get(pk=person_id)
            liste = []
            for e1 in Entree.objects.filter(User=personne):
                e1s = e1.sortie
                if e1s == None:
                    e1s = timezone.datetime.now().replace(tzinfo=pytz.utc)
                for e2 in Entree.objects.all():
                    e2s = e2.sortie
                    if e2s == None:
                        e2s = timezone.datetime.now().replace(tzinfo=pytz.utc)
                    if e1.entree <= e2.entree <=e1s or e1.entree <= e2s <=e1s:
                        if e2.User != personne and e1.salle == e2.salle:
                            liste.append(e2)

            return render(request, 'pointage/containfo.html',{"personnes" : liste, "personne":personne})
        except User.DoesNotExist:
            return redirect("conta")
    else:
        redirect(request, "index")

def getGant():
    entries = PrevEntree.objects.all()
    now = timezone.now().replace(tzinfo=pytz.utc)
    pio.renderers.default = 'browser'
    df = []
    for entree in entries:
        if entree.entree > now or  entree.entree.day==now.day:
            df.append(dict(Personne=entree.User.first_name+" "+entree.User.last_name, Start=entree.entree, Finish=entree.sortie,Salle=entree.get_salle_display()))
        else:
            entree.delete()
    if len(df)==0:
        return None
    colors = {"Bureau d'étude": 'rgb(80, 15, 15)',
              'Découpe laser':'rgb(32,72,13)',
              'Atelier': 'rgb(17, 23, 57)'}
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Personne",hover_data={"Start": "| %A %B %d, %Hh%M"}, color="Salle")
    fig.update_layout(
        title='Planning de réservation des salles',

    )
    return plot(fig, output_type="div")

def prev(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ReserveForm(request.POST)
            if form.is_valid() :
                dentree = form.cleaned_data.get('entree')
                dsortie = form.cleaned_data.get('sortie')
                dentree = dentree.replace(tzinfo=pytz.utc)
                dsortie = dsortie.replace(tzinfo=pytz.utc)
                if dsortie > dentree:
                    if dsortie <= dentree + datetime.timedelta(hours=8):

                        resa = PrevEntree(entree=dentree, sortie=dsortie-timezone.timedelta(seconds=1), User=request.user, salle=form.cleaned_data.get('salle'))
                        resa.save()
                        return render(request, 'pointage/prevpassage.html', {"form": ReserveForm(), "gant":getGant(),"occup":getOccupancyTab(), "success":"Créneau réservé avec succès"})
                    return render(request, 'pointage/prevpassage.html', {"form": ReserveForm(), "gant":getGant(),"occup":getOccupancyTab(), "error":"Vous ne pouvez pas réserver un créneau de plus de 8 heures"})
                return render(request, 'pointage/prevpassage.html',{"form": ReserveForm(), "gant":getGant(),"occup":getOccupancyTab(), "error": "La date de sortie doit être après la date d'entrée"})
            return render(request, 'pointage/prevpassage.html',{"form": ReserveForm(), "gant":getGant(),"occup":getOccupancyTab(), "error": "Veuillez entrer une date, aidez vous du sélectionneur"})
        return render(request, 'pointage/prevpassage.html', {"form": ReserveForm(), "gant":getGant(),"occup":getOccupancyTab()})
    return redirect("index")

def changepasssword(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                if form.cleaned_data.get("passw") == form.cleaned_data.get("passw2"):
                    success ="Votre mot de passe a été changé"
                    u = request.user
                    u.set_password(form.cleaned_data.get("passw"))
                    u.save()

                    if request.user.is_staff:
                        return render(request, 'pointage/account.html', {"staff": "", "pseudo": request.user.username,"success":success})

                    return render(request, 'pointage/account.html',{"success":success})
                return render(request, 'pointage/changepassword.html', {"error": "Veuillez entrer 2 fois le même mot de passe","form": ChangePasswordForm()})
            return render(request, 'pointage/changepassword.html', {"error": "Veuillez entrer 2 fois le même mot de passe","form": ChangePasswordForm()})
        return render(request, 'pointage/changepassword.html', {"form": ChangePasswordForm()})
    return redirect(index)

def getOccupancyTab():
    dfs={"Atelier" : [], "Bureau d'étude" : [], "Découpe laser":[]}
    temp_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0,tzinfo=pytz.utc)
    index = [(temp_day + datetime.timedelta(minutes=d * 30)) for d in range(350)]
    for entree in PrevEntree.objects.all():
        if str(entree.sortie) < str(index[-1]):
            dfs[entree.get_salle_display()].append([str(entree.entree),str(entree.sortie)])
    dfs["Atelier"]=pd.DataFrame(dfs["Atelier"],columns=['start', 'end'])
    dfs["Bureau d'étude"] = pd.DataFrame(dfs["Bureau d'étude"], columns=['start', 'end'])
    dfs["Découpe laser"] = pd.DataFrame(dfs["Découpe laser"], columns=['start', 'end'])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        visible=False,
        x=index,
        y=computeOccupancy(dfs["Bureau d'étude"],index,_LIMIT_BE),
        name="Bureau d'étude",
        marker_color='indianred',
    ))
    fig.add_trace(go.Bar(
        visible=False,
        x=index,
        y=computeOccupancy(dfs["Atelier"],index,_LIMITE_A),
        name='Atelier',
        marker_color='lightblue'
    ))
    fig.add_trace(go.Bar(
        visible=False,
        x=index,
        y=computeOccupancy(dfs["Découpe laser"], index, _LIMITE_DL),
        name="Découpe laser",
        marker_color='lightgreen'
    ))
    salles=[ "Bureau d'étude","Atelier", "Découpe laser" ]

    fig.data[0].visible = True
    # Here we modify the tickangle of the xaxis, resulting in rotated labels.

    steps = []

    for i in range(3):
        step = dict(method='restyle',
                    args=['visible', [False] * 3],
                    label=salles[i],
                    )  # label to be displayed for each step (year)
        step['args'][1][i] = True
        steps.append(step)

    ##  I create the 'sliders' object from the 'steps'

    sliders = [dict(active=0, pad={"t": 50}, steps=steps)]



    fig.update_layout(
        sliders=sliders,
        bargap = 0.001,
        title='Occupation des salles (en %)',
    )

    return plot(fig, output_type="div")




def computeOccupancy(df,index,tresh):

    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])

    # ---- Create day index


    # ---- Create empty result df
    # initialize df, set days as datetime in index
    d = pd.DataFrame(np.zeros((350, 3)),
                     index=pd.to_datetime(index),
                     columns=['new_visitor', 'occupancy', 'occupied_day'])

    # ---- Iterate over df to fill d (final df)
    for i, row in df.iterrows():
        # Add 1 for visitor occupancy these days
        d.loc[row.start:row.end, 'occupancy'] += 1
        tresh=100/tresh
    return d["occupancy"].astype(float)*tresh

def delete(request,resa_id):
    resa = PrevEntree.objects.get(id=resa_id)
    resa.delete()
    return redirect("account")

def update(request):
    if request.user.is_staff and request.user.last_name == "Forestier":
        for entree in Entree.objects.all():
            entree.entree = entree.entree.replace(tzinfo=pytz.utc)
            entree.sortie = entree.sortie.replace(tzinfo=pytz.utc) if entree.sortie!=None else ""
            entree.save()
        for entree in PrevEntree.objects.all():
            entree.entree = entree.entree.replace(tzinfo=pytz.utc)
            entree.sortie = entree.sortie.replace(tzinfo=pytz.utc)
            entree.save()
    return redirect("index")

def impor(request):
    if request.user.is_staff and request.user.last_name == "Forestier":
        fichier = open("server_output.csv","r")
        for ligne in fichier:
            info = ligne.split(",")
            user = User.objects.create_user(info[0], '', info[1])
            user.last_name = info[2]
            user.first_name=info[3]
            user.save()
            asso = Asso(user=user,color=info[4])
            asso.save()
    return redirect("index")


