from django.urls import path
from . import views

urlpatterns = [
    path('add_trip/', views.add_trip, name='add_trip'),
    path('trip_listing/', views.trip_listing, name='trip_listing'),
    path('trip_details/<str:trip_id>/', views.trip_details, name='trip_details'),
]
