from django.urls import path
from . import views

urlpatterns = [
    path('add_booking/', views.add_booking, name='add_booking'),
    path('booking_listing/', views.booking_listing, name='booking_listing'),
    path('booking_details/<str:ticket_id>/', views.booking_details, name='booking_details'),
]
