from django.urls import path
from . import views


urlpatterns = [
    path('phishing_test/<int:test_id>/track/<int:employee_id>/<str:token>/', views.track_action, name='track_action'),
]