from django.db import models
import re
from django.core.exceptions import ValidationError

class Route(models.Model):
    route_id = models.CharField(primary_key=True, max_length=10)  #PK
    user_id = models.CharField(max_length=10)
    route_name = models.CharField(max_length=100,null=False)
    route_origin = models.CharField(max_length=100,null=False)
    route_destination = models.CharField(max_length=100,null=False)
    stops = models.JSONField()  

#added model level validation for data integrity

    def clean(self):
        if not self.route_id.startswith('RT'):
            raise ValidationError("Route ID must start with 'RT'.")
        if not re.match(r'^RT\d{8}$', self.route_id):
            raise ValidationError("Invalid route ID format. It should be 'RT' followed by 8 digits.")



