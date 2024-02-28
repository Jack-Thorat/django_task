from django.db import models
import re
from django.core.exceptions import ValidationError
from route.models import Route 

class Trip(models.Model):
    trip_id = models.CharField(primary_key=True, max_length=10)
    user_id = models.CharField(max_length=10)
    vehicle_id = models.CharField(max_length=10)
    route = models.ForeignKey(Route, on_delete=models.DO_NOTHING, blank=True, null=True)
    driver_name = models.CharField(max_length=100)
    trip_distance = models.DecimalField(max_digits=10, decimal_places=2)

# added model level validation for data integrity
    def clean(self):

        if not self.trip_id.startswith('TP'):
            raise ValidationError("Trip ID must start with 'TP'.")
        if not re.match(r'^TP\d{8}$', self.trip_id):
            raise ValidationError("Invalid trip ID format. It should be 'TP' followed by 8 digits.")

