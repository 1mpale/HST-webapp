from django.urls import path
from . import views

urlpatterns = [
    path('',views.index),
    path('predict', views.prediction),
    path('visualize', views.visualization),
    
]
