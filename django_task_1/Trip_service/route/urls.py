from django.urls import path
from . import views

urlpatterns = [
    path('add_route/', views.add_route, name='add_route'),
    path('route_listing/', views.route_listing, name='route_listing'),
    path('route_details/<str:route_id>/', views.route_details, name='route_details'),
]
