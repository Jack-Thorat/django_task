import json
from django.http import JsonResponse, HttpResponse
from .models import Trip, Route
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
from django.core.exceptions import ValidationError
from django.db.models import Q
import requests

@csrf_exempt
def add_trip(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Check if all required fields are present and not blank
            required_fields = ['user_id', 'vehicle_id', 'driver_name', 'trip_distance', 'trip_id', 'route_id']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Validate trip_id format
            if not re.match(r'^TP\d{8}$', data['trip_id']):
                return JsonResponse({'error': 'Invalid trip_id format. It should start with TP followed by 8 digits'}, status=400)

            # Check if the route exists
            route_id = data['route_id']
            if not Route.objects.filter(route_id=route_id).exists():
                return JsonResponse({'error': f'Route with route_id {route_id} does not exist'}, status=400)

            # Check if the trip already exists
            if Trip.objects.filter(route_id=route_id).exists():
                return JsonResponse({'error': f'Trip with route_id {route_id} already exists'}, status=400)

            # Add trip to the database
            trip = Trip.objects.create(
                trip_id=data['trip_id'],
                user_id=data['user_id'],
                vehicle_id=data['vehicle_id'],
                route_id=route_id,
                driver_name=data['driver_name'],
                trip_distance=data['trip_distance']
            )
            return JsonResponse({'message': 'Trip added successfully', 'trip_id': trip.trip_id}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return HttpResponse(status=405)

@csrf_exempt
def trip_listing(request):
    if request.method == 'GET':
        # Fetch all trips with associated route data
        trips = Trip.objects.select_related('route').all()

        # Apply search filter based on query parameters
        query = request.GET.get('query')
        if query:
            trips = trips.filter(
                Q(driver_name__icontains=query) |
                Q(user_id__icontains=query) |
                Q(vehicle_id__icontains=query) |
                Q(route__route_name__icontains=query) |
                Q(route__route_origin__icontains=query) |
                Q(route__route_destination__icontains=query) |
                Q(trip_id__exact=query) |
                Q(route_id__exact=query)
                )

        # Sorting, pagination logic
        page_number = request.GET.get('page', 1)
        paginator = Paginator(trips, 10)  # Show 10 trips per page
        try:
            trips = paginator.page(page_number)
        except PageNotAnInteger:
            trips = paginator.page(1)
        except EmptyPage:
            trips = paginator.page(paginator.num_pages)
        
        data = {
            'trips': [],
            'has_next': trips.has_next(),
            'has_previous': trips.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': trips.number
        }

        # Fetch booking details for each trip
        for trip in trips:
            trip_data = {
                "trip_id": trip.trip_id,
                "user_id": trip.user_id,
                "vehicle_id": trip.vehicle_id,
                "driver_name": trip.driver_name,
                "trip_distance": trip.trip_distance,
                "route": {
                    "route_id": trip.route.route_id,
                    "route_name": trip.route.route_name,
                    "route_origin": trip.route.route_origin,
                    "route_destination": trip.route.route_destination,
                    "stops": trip.route.stops
                },
                "bookings": []  # Initialize empty list for bookings
            }
            booking_service_url = f'http://127.0.0.1:8001/booking_listing/?query={trip.trip_id}'
            booking_response = requests.get(booking_service_url)
            if booking_response.status_code == 200:
                booking_data = booking_response.json().get('bookings', [])
                trip_data['bookings'] = booking_data

            data['trips'].append(trip_data)

        return JsonResponse(data)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def trip_details(request, trip_id):
    if request.method == 'GET':
        try:
            # Fetch trip details
            trip = Trip.objects.get(trip_id=trip_id)
            data = {
                "trip": {
                    "trip_id": trip.trip_id,
                    "user_id": trip.user_id,
                    "vehicle_id": trip.vehicle_id,
                    "driver_name": trip.driver_name,
                    "trip_distance": trip.trip_distance,
                    "route_id": trip.route.route_id
                }
            }
            return JsonResponse(data)
        except Trip.DoesNotExist:
            return JsonResponse({'error': 'Trip not found'}, status=404)
    else:
        return HttpResponse(status=405)
