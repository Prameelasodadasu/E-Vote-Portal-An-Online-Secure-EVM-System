from django.urls import path
from . import views

urlpatterns = [
    path('active/', views.active_elections),
    path('<int:election_id>/ballot/', views.ballot),
]
