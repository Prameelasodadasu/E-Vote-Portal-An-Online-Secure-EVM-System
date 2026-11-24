from django.urls import path
from . import views

urlpatterns = [
    path('<int:election_id>/cast/', views.cast_vote),
]
