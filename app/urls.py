"""
URL routing for the FlowMarket app
Maps URLs to their corresponding view functions
"""
from django.urls import path
from . import views

app_name = 'flow_market'

urlpatterns = [
    # Home page - dashboard, stats, and quick links
    path('', views.home, name='home'),

    # USSD webhook endpoint - Africa's Talking POST requests
    path('ussd', views.ussd_callback, name='ussd_callback'),

    # Manual SMS campaign trigger - can be accessed via browser/API
    path('send-campaign', views.send_campaign_view, name='send_campaign'),

    # Products API endpoint - returns active products in JSON
    path('products/', views.products_list, name='products_list'),
]
