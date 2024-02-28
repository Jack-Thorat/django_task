from django.http import JsonResponse, HttpResponse
from .models import Route
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
import re
from django.db.models import Q

@csrf_exempt
def add_route(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Check if all required fields are present and not blank
            required_fields = ['route_id', 'user_id', 'route_name', 'route_origin', 'route_destination', 'stops']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'{field.capitalize()} is required and cannot be blank'}, status=400)

            # Validate input data
            # Validate route_id format
            if not data['route_id'].startswith('RT') or not re.match(r'^RT\d{8}$', data['route_id']):
                return JsonResponse({'error': 'Invalid route_id format. It should start with RT followed by 8 digits'}, status=400)

            # Add to the database
            route = Route.objects.create(
                route_id=data['route_id'],
                user_id=data['user_id'],
                route_name=data['route_name'],
                route_origin=data['route_origin'],
                route_destination=data['route_destination'],
                stops=data['stops']
            )
            return JsonResponse({'message': 'Route added successfully', 'route_id': route.route_id}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return HttpResponse(status=405)




    
@csrf_exempt
def route_listing(request):
    if request.method == 'GET':
        # Fetch all routes
        routes = Route.objects.all()

        # Apply search filter based on query parameters
        query = request.GET.get('query')
        if query:
            routes = routes.filter(
                Q(route_id__icontains=query) |
                Q(route_name__icontains=query) |
                Q(route_origin__icontains=query) |
                Q(route_destination__icontains=query)
            )

        # Sorting
        sort_by = request.GET.get('sort_by', 'route_id')  # Default sort by route_id
        if sort_by in ['route_id', 'route_name', 'route_origin', 'route_destination']:
            routes = routes.order_by(sort_by)

        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(routes, 10)  # Showing 10 routes per page
        try:
            routes_page = paginator.page(page_number)
        except PageNotAnInteger:
            routes_page = paginator.page(1)
        except EmptyPage:
            routes_page = paginator.page(paginator.num_pages)

        # Extract values from routes in the current page
        routes_data = []
        for route in routes_page:
            route_data = {
                "route_id": route.route_id,
                "user_id": route.user_id,
                "route_name": route.route_name,
                "route_origin": route.route_origin,
                "route_destination": route.route_destination,
                "stops": route.stops
            }
            routes_data.append(route_data)

        # Prepare response data
        data = {
            'routes': routes_data,
            'has_next': routes_page.has_next(),
            'has_previous': routes_page.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': routes_page.number
        }
        return JsonResponse(data)
    else:
        return HttpResponse(status=405)



@csrf_exempt
def route_details(request, route_id):
    if request.method == 'GET':
        try:
            route = Route.objects.get(route_id=route_id)
            data = {"route": {
                "route_id": route.route_id,
                "user_id": route.user_id,
                "route_name": route.route_name,
                "route_origin": route.route_origin,
                "route_destination": route.route_destination,
                "stops": route.stops
            }}
            return JsonResponse(data)
        except Route.DoesNotExist:
            return JsonResponse({'error': 'Route not found'}, status=404)
    else:
        return HttpResponse(status=405)
