from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Include all patterns from App app folder
    path('', include('App.App.urls')),
]
