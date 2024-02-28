# booking/models.py
from django.db import models
import re
from django.core.exceptions import ValidationError
from django.conf import settings

class Booking(models.Model):
    ticket_id = models.CharField(primary_key=True, max_length=10)
    trip_id = models.CharField(max_length=10)  
    traveller_name = models.CharField(max_length=100)
    traveller_number = models.CharField(max_length=15)
    ticket_cost = models.DecimalField(max_digits=10, decimal_places=2)
    traveller_email = models.EmailField()

    def clean(self):
        # Validate ticket_id format
        if not self.ticket_id.startswith('TK'):
            raise ValidationError("Ticket ID must start with 'TK'.")
        if not re.match(r'^TK\d{8}$', self.ticket_id):
            raise ValidationError("Invalid ticket ID format. It should be 'TK' followed by 8 digits.")

        # Validate traveller_number format
        if not re.match(r'^\d{10}$', self.traveller_number):
            raise ValidationError("Invalid phone number format. It should contain 10 digits.")
'''
    def get_trip_details(self):
        # Fetch trip details from Trip service using inter-service call
        trip_id = self.trip_id
        if trip_id:
            trip_service_url = settings.TRIP_SERVICE_URL  # URL of Trip service endpoint
            response = requests.get(f"{trip_service_url}/trip-details/{trip_id}")
            if response.status_code == 200:
                return response.json()
        return None
'''