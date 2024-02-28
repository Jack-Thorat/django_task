import requests
import json
import re
from django.http import JsonResponse, HttpResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Booking
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.db.models import Q

@csrf_exempt
def add_booking(request):

    
    if request.method == 'POST':
        try:
            # deserialization
            received_data = json.loads(request.body)

            
            # Validate input data
            required_fields = ['ticket_id', 'traveller_name', 'traveller_number', 'ticket_cost', 'traveller_email', 'trip_id']
            missing_fields = [field for field in required_fields if field not in received_data]
            if missing_fields:
                return JsonResponse({'error': f'Missing required field(s): {", ".join(missing_fields)}'}, status=400)
            
            # Validate ticket_id format
            if not re.match(r'^TK\d{8}$', received_data['ticket_id']):
                return JsonResponse({'error': 'Invalid ticket_id format. It should start with TK followed by 8 digits'}, status=400)
            
            # Validate trip_id format
            if not re.match(r'^TP\d{8}$', received_data['trip_id']):
                return JsonResponse({'error': 'Invalid trip_id format. It should start with TP followed by 8 digits'}, status=400)
            
            # Validate traveller_number format
            if not re.match(r'^\d{10}$', received_data['traveller_number']):
                return JsonResponse({'error': 'Invalid traveller_number format. It should be a 10-digit number'}, status=400)
            
            # Validate traveller_email format
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', received_data['traveller_email']):
                return JsonResponse({'error': 'Invalid traveller_email format'}, status=400)
            
            # Check if the trip_id already exists in the database
            if Booking.objects.filter(trip_id=received_data['trip_id']).exists():
                return JsonResponse({'error': 'Trip ID already exists'}, status=400)
            
            # Fetch trip details to validate if the trip_id exists
            trip_service_url = f'http://localhost:8000/trip_details/{received_data["trip_id"]}/'
            trip_response = requests.get(trip_service_url)
            
            if trip_response.status_code == 200:
                trip_data = trip_response.json()
                trip_id = trip_data.get('trip', {}).get('trip_id')
                if trip_id != received_data['trip_id']:
                    return JsonResponse({'error': 'Provided trip_id does not match the trip_id from the trip service'}, status=400)
            else:
                return JsonResponse({'error': 'Invalid trip_id or trip does not exist'}, status=400)
            
            # Add booking to the database
            booking = Booking.objects.create(
                ticket_id=received_data['ticket_id'],
                trip_id=received_data['trip_id'],
                traveller_name=received_data['traveller_name'],
                traveller_number=received_data['traveller_number'],
                ticket_cost=received_data['ticket_cost'],
                traveller_email=received_data['traveller_email']
            )
            
            return JsonResponse({'message': 'Booking added successfully', 'ticket_id': booking.ticket_id}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        except ValidationError as e:

            return JsonResponse({'error': str(e)}, status=400)
        
        except IntegrityError:

            return JsonResponse({'error': 'Provided ticket_id already exists or does not follow the format'}, status=400)
    
    else:

        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)



@csrf_exempt
def booking_listing(request):
    if request.method == 'GET':
        # Sorting
        sort_by = request.GET.get('sort_by', 'ticket_id')  # Default sort by ticket_id
        if sort_by in ['ticket_id', 'traveller_name', 'ticket_cost', 'traveller_number', 'traveller_email', 'trip_id']:
            bookings = Booking.objects.all().order_by(sort_by)

        # Searching used Q for complex query searches with logical or
        query = request.GET.get('query')
        if query:
            bookings = bookings.filter(
                Q(traveller_name__icontains=query) |
                Q(ticket_id__icontains=query) |
                Q(ticket_cost__icontains=query) |
                Q(traveller_number__icontains=query) |
                Q(traveller_email__icontains=query) |
                Q(trip_id__icontains=query)
            )

        # Pagination
        paginator = Paginator(bookings, 10)  # Show 10 bookings per page
        page = request.GET.get('page', 1)
        try:
            page = int(page)
        except ValueError:
            page = 1
        try:
            bookings = paginator.page(page)
        except PageNotAnInteger:
            bookings = paginator.page(1)
        except EmptyPage:
            bookings = paginator.page(paginator.num_pages)

        data = {"bookings": list(bookings.object_list.values())}
        return JsonResponse(data)
    else:
        return HttpResponse(status=405)



@csrf_exempt
def booking_details(request, ticket_id):
    if request.method == 'GET':
        try:
            # Fetch booking details
            booking = Booking.objects.get(ticket_id=ticket_id)
            
            # Fetch trip details using the trip_id from the booking
            trip_id = booking.trip_id
            trip_details_url = f'http://127.0.0.1:8000/trip_details/{trip_id}/'
            trip_response = requests.get(trip_details_url)
            
            if trip_response.status_code == 200:
                trip_data = trip_response.json().get('trip', {})
                route_id = trip_data.get('route_id')  # Get route_id from trip data
                print("Trip Data:", trip_data)  # Debugging: Print trip data
                print("Route ID:", route_id)  # Debugging: Print route id
            else:
                trip_data = {}
                route_id = None
            
            if route_id:
                # Fetch route details using the route_id from the trip data
                route_details_url = f'http://127.0.0.1:8000/route_details/{route_id}/'
                route_response = requests.get(route_details_url)
                
                if route_response.status_code == 200:
                    route_data = route_response.json().get('route', {})
                else:
                    route_data = {}
            else:
                route_data = {}
            
            data = {
                "booking": {
                    "ticket_id": booking.ticket_id,
                    "trip_id": booking.trip_id,
                    "traveller_name": booking.traveller_name,
                    "traveller_number": booking.traveller_number,
                    "ticket_cost": booking.ticket_cost,
                    "traveller_email": booking.traveller_email
                },
                "trip": trip_data,  # Include trip details fetched from the endpoint
                "route": route_data  # Include route details fetched from the endpoint
            }
            return JsonResponse(data)
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
    else:
        return HttpResponse(status=405)
