"""
Main project URL Configuration
Routes requests to the appropriate app
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin - for managing contacts
    path('admin/', admin.site.urls),
    
    # Include all routes from our app
    path('', include('app.urls')),
]
