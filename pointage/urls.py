from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('<int:person_id>/entry', views.entry, name='Marquage Entrée'),
    path('<int:person_id>/exit', views.exit, name='Marquage Sortie'),
    path('<int:person_id>/index', views.backindex, name='indexbis'),
    path('account', views.account, name='account'),
    path('logout', views.logout, name='logout'),
    path('<int:person_id>/account', views.backaccount, name='accountbis'),
    path('conta', views.conta, name='conta'),
    path('nextpassage', views.prev, name='prev'),
    path('<int:person_id>/nextpassage', views.backprev, name='backprev'),
    path('<int:person_id>/conta', views.containfo, name='infos'),
    path('changepassword',views.changepasssword,name="changepassword"),
    path('<int:resa_id>/delete',views.delete,name="delete"),
    path('import',views.impor,name="delete"),
    path('update',views.update, name = "update")
]