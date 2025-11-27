"""
URL routing for the app
Maps URLs to view functions
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home page - shows info and links
    path('', views.home, name='home'),
    
    # USSD webhook endpoint - receives POST requests from Africa's Talking
    path('ussd/', views.ussd_callback, name='ussd_callback'),
    
    # Manual SMS campaign trigger - can be accessed via browser
    path('send-campaign/', views.send_campaign_view, name='send_campaign'),
]
