# django
from django.db import models
from django.utils import timezone
from django.urls import reverse
# https://docs.djangoproject.com/en/5.1/topics/db/aggregation/
from django.db.models import Avg, Count, Min, Sum
from django.db.models.functions import ExtractYear

# other
import json
import hashlib
import pytz
from datetime import datetime
# self
from .microservice import MicroserviceInterface

class JSONModel(models.Model):
    """Custom constructor to populate properties from JSON
    
    Goes through the class properties, if field exists in
    JSON object, it assigns its value to the property.
    
    """
    class Meta:
        # Ensures this model is not created in the database
        abstract = True

    def __init__(self, *args, json_data=None, **kwargs):
        super(JSONModel, self).__init__(*args, **kwargs)
        # If a JSON object is passed, populate fields generically
        if json_data:        
            self._assign_props_from_json(json_data)

    def _assign_props_from_json(self,json_data):
        # Iterate through the model's fields and set attributes
        for field in self._meta.get_fields():
            field_name = field.name
            # skip django fields
            if field_name in ["id"]:
                continue
            if field_name in json_data:
                # some fields have {value: ..., unit: ... } sub structure
                try:
                    value = json_data[field_name]["value"]
                except:
                    value = json_data[field_name]
                # all absolute times are UTC
                if isinstance(field, models.DateTimeField):
                    # Convert the string to a timezone-aware datetime object
                    value = self.convert_to_utc_datetime(value)
                # finally, assign
                setattr(self, field_name, value)

    def convert_to_utc_datetime(self, date_str):
        # Define the format of the date string from the JSON
        date_format = "%Y-%m-%d %H:%M:%S"  # Adjust format if needed
        # Parse the string into a naive datetime object
        naive_datetime = datetime.strptime(date_str, date_format)
        # Assign the UTC timezone
        utc_timezone = pytz.utc
        # Convert the naive datetime to a timezone-aware one
        return utc_timezone.localize(naive_datetime)


class FlightManager(models.Manager):
    def get_unique_years(self):
        """Return unique list of years, based on takeoff time stamp"""
        # Annotate year from related Takeoff 'time' field
        q = Flight.objects.annotate(year=ExtractYear('takeoff__time'))
        # Extract unique
        q = q.values('year').distinct()
        # QuerySet > regular list
        unique_years = list(q.values_list('year', flat=True))
        return unique_years
    
    def get_airtime_total(self):
        t_sec = Flight.objects.aggregate(Sum("airtime")).get('airtime__sum', 0)
        return t_sec / 3600 # time in hours

    def get_airtime_for_year(self,year):
        """Return airtime in hours, 0 if no flights in year"""
        q = Flight.objects.filter(takeoff__time__year=year)
        t_sec = q.aggregate(Sum("airtime")).get('airtime__sum', 0)
        return t_sec/3600 # time in hours
    
    def get_flights_total(self):
        return Flight.objects.count()
    
    def get_flights_for_year(self,year):
        """Return number of flights, 0 if no flights in year"""
        q = Flight.objects.filter(takeoff__time__year=year)
        return q.count()


# Create your models here.
class Flight(JSONModel):
    """Root model"""

    # custom manager
    objects = FlightManager()

    # properties
    file = models.FileField(upload_to='igc_files/')
    # SHA256 - field throws error if hash already exists
    file_hash = models.CharField(max_length=64, unique=True)
    # flight import datetime
    import_datetime = models.DateTimeField(auto_now_add=True)
    
    # -----------------------------------------------------
    # unpack json data
    #
    #  "airtime_str": "6:44:35",
    airtime_str = models.CharField(max_length=255,null=True)
    #  "airtime": {
    #    "value": 24275.0,
    #    "unit": "s"
    #  }
    airtime = models.FloatField(null=True)

    def init_from_file(self,igc_file):
        """  """
        self.file = igc_file
        self.save() # write and close file
        self._compute_file_hash()
        # process uploaded file
        msi = MicroserviceInterface()
        self._xc_metrics_response(
            msi.xc_metrics_service(self.file)
        )
        self._xc_score_response(
            msi.xc_score_service(self.file)
        )
        self.save()

    def _compute_file_hash(self):
        """Reads the file, computes the SHA-256 hash, and stores it in 
        the file_hash field.
        """
        if not self.file:
            return None
        # Open the file and read its content in chunks to avoid memory 
        # issues with large files
        sha256_hash = hashlib.sha256()
        self.file.open('rb')  # Ensure the file is opened in binary mode
        # Read the file in chunks to avoid memory issues with large files
        for chunk in iter(lambda: self.file.read(4096), b""):
            sha256_hash.update(chunk)
        # Compute the hash and store it in file_hash
        self.file_hash = sha256_hash.hexdigest()
        # rewind so file can be read again
        self.file.seek(0)

    def _xc_metrics_response(self,d):
        """" create children from xc-metrics json response"""
        # unpack json data into one-to-one properties
        self._assign_props_from_json(json_data=d["info"]["flight"])
        Takeoff.objects.create(parent=self,json_data=d["info"]["takeoff"])
        Landing.objects.create(parent=self,json_data=d["info"]["landing"])
        Thermals.objects.create(parent=self,json_data=d["info"]["thermals"])
        Glides.objects.create(parent=self,json_data=d["info"]["glides"])
        # set remaining properties manually
        self.glides.geojson = d["glides"]
        self.thermals.geojson = d["thermals"]
        # save everything
        self.takeoff.save()
        self.landing.save()
        self.thermals.save()
        self.glides.save()
        self.save()

    def _xc_score_response(self,d):
        """"Create children from comp-metrics json response"""
        XCScore.objects.create(parent=self,json_data=d["properties"])
        self.xcscore.geojson = d
        self.xcscore.save()

    def _a_href(self,link_text):
        """Return a html link element to this flights detail page"""
        return f'<a href=" \
            {reverse('frontend:flight_detail', args=[self.id])}"> \
            {link_text}</a>'

    @property
    def to_geojson_feature_point(self):
        if not self.takeoff:
            return {}
        popup = f"<ul>\
            <li>{self.takeoff.time.date()}</li>\
            <li>{self.airtime_str} h</li>\
            <li>{self.xcscore.type} {self.xcscore.score} p</li>\
            <li>{self._a_href('Flight detail')}</li>\
            </ul>"
        return {
            "type": "Feature",
            "properties": {
                "popupContent": popup
            },
            "geometry": {
                "type": "Point",
                "coordinates": [self.takeoff.lon, self.takeoff.lat]
            }
        }
        
    @property
    def file_hash_short(self):
        """Return the first 5 characters of file_hash or an empty 
        string if not set."""
        if self.file_hash:
            return self.file_hash[:6]
        return ""

    @property
    def takeoff_short(self):
        if hasattr(self,"takeoff"):
            if self.takeoff.name: # not empty
                return f"{self.takeoff.country.upper()} {self.takeoff.name[:15]}"
        return ""

    def __str__(self):
        s = f"{self.file_hash_short} {self.airtime_str}"
        s += f" {self.xcscore.code}" if hasattr(self,"xcscore") else ""
        s += f" {self.xcscore.score}" if hasattr(self,"xcscore") else ""
        s += f" {self.takeoff_short}" if self.takeoff_short else ""
        return s

class XCScore(JSONModel):
    """ igc-xc-score info"""
    # belongs to flight
    parent = models.OneToOneField(Flight, on_delete=models.CASCADE)
    # GeoJSON data
    geojson = models.JSONField(null=True)
    # -----------------------------------------------------
    # unpack json data
    #
    #  "properties": {
    #  "name": "EPSG:3857",
    #  "id": 1369,
    #  "score": 208.94, # points
    score = models.FloatField(null=True)
    #  "bound": 208.96,
    #  "optimal": true,
    #  "processedTime": 0.319,
    #  "processedSolutions": 802,
    #  "type": "Closed FAI Triangle",
    type = models.CharField(max_length=255,null=True)
    #  "code": "fai"
    code = models.CharField(max_length=255,null=True)

    # todo
    # igc-xc-score console output:
    # Launch at fix 0, 09:33:15                                                                             
    # Landing at fix n-0 16:18:12
    # TP1 : TP2 :    37.05km (37.053km)
    # TP2 : TP3 :    51.22km (51.223km)
    # TP3 : TP1 :    44.05km (44.052km)
    # Best solution is optimal Triangle FAI 185.25 points, 132.32km
    # Multiplier is 1.4 [ closing distance is 1.73km ]

class Takeoff(JSONModel):
    # belongs to flight
    parent = models.OneToOneField(Flight, on_delete=models.CASCADE)

    # -----------------------------------------------------
    # unpack json data
    #
    # "name": "Col d'Izoard"
    name = models.CharField(max_length=255)
    # "country": "fr"
    country = models.CharField(max_length=2)
    # "dist": {
    #   "value": 70.53027327496399,
    #   "unit": "m"
    # }
    dist = models.FloatField()
    # "time": {
    #   "value": "2024-08-05 09:33:15",
    #   "unit": "UTC"
    # }
    time = models.DateTimeField()
    # "lat": {
    #   "value": 44.81906666666667,
    #   "unit": "deg"
    # }
    lat = models.FloatField()
    # "lon": 
    #   "value": 6.7287
    #   "unit": "deg
    # },
    lon = models.FloatField()
    # "alt_gnss": {
    #   "value": 2444.0,
    #   "unit": "m"
    # }
    alt_gnss = models.FloatField()

class Landing(JSONModel):
    # belongs to flight
    parent = models.OneToOneField(Flight, on_delete=models.CASCADE)

    # -----------------------------------------------------
    # unpack json data
    #
    # "time": {
    #   "value": "2024-08-05 09:33:15",
    #   "unit": "UTC"
    # }
    time = models.DateTimeField()
    # "lat": {
    #   "value": 44.81906666666667,
    #   "unit": "deg"
    # }
    lat = models.FloatField()
    # "lon": 
    #   "value": 6.7287
    #   "unit": "deg
    # },
    lon = models.FloatField()
    # "alt_gnss": {
    #   "value": 2444.0,
    #   "unit": "m"
    # }
    alt_gnss = models.FloatField()

class Thermals(JSONModel):
    # belongs to flight
    parent = models.OneToOneField(Flight, on_delete=models.CASCADE)
    # GeoJSON data
    geojson = models.JSONField(null=True)

    # -----------------------------------------------------
    # unpack json data
    #
    # "time_total": {
    #   "value": 0.2533470648815654,
    #   "unit": "%"
    # },
    time_total = models.FloatField()
    # "max_avg_climb": {
    #   "value": 3.7967914438502675,
    #   "unit": "m/s"
    # },
    max_avg_climb = models.FloatField()
    # "max_gain": {
    #   "value": 710.0,
    #   "unit": "m"
    # },
    max_gain = models.FloatField()
    # "circ_dir_L": {
    #   "value": 0.6395121951219512,
    #   "unit": "%"
    # },
    circ_dir_L = models.FloatField()
    # "circ_dir_R": {
    #   "value": 0.09073170731707317,
    #   "unit": "%"
    # },
    circ_dir_R = models.FloatField()
    # "circ_dir_LR": {
    #   "value": 0.2697560975609756,
    #   "unit": "%"
    # }
    circ_dir_LR = models.FloatField()

class Glides(JSONModel):
    # belongs to flight
    parent = models.OneToOneField(Flight, on_delete=models.CASCADE)
    # GeoJSON data
    geojson = models.JSONField(null=True)

    # -----------------------------------------------------
    # unpack json data
    #
    # "time_total": {
    #   "value": 0.7466529351184346,
    #   "unit": "%"
    # },
    time_total = models.FloatField()
    # "avg_speed": {
    #   "value": 38.74671592015784,
    #   "unit": "km/h"
    # }
    avg_speed = models.FloatField()
