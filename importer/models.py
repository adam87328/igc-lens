from django.db import models
from django.urls import reverse
# https://docs.djangoproject.com/en/5.1/topics/db/aggregation/
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.db.models.functions import ExtractYear

from datetime import timedelta
from .util import *

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
                    value = convert_to_utc_datetime(value)
                # durations are in seconds
                if isinstance(field, models.DurationField):
                    value = timedelta(seconds=value)
                # finally, assign
                setattr(self, field_name, value)


class FlightManager(models.Manager):
    def get_unique_years(self):
        """Return unique list of years, based on takeoff time stamp"""
        # Annotate year from related Takeoff 'time' field
        q = Flight.objects.annotate(year=ExtractYear('takeoff__datetime'))
        # Extract unique
        q = q.values('year').distinct()
        # QuerySet > regular list
        unique_years = list(q.values_list('year', flat=True))
        unique_years.sort()
        return unique_years
    
    def get_airtime_total(self):
        """Return airtime in hours"""
        t_sec = Flight.objects.aggregate(Sum("airtime")).get('airtime__sum', 0)
        return t_sec / 3600
        
    def get_airtime_for_year(self,year):
        """Return airtime in hours, 0 if no flights in year"""
        q = Flight.objects.filter(takeoff__datetime__year=year)
        t_sec = q.aggregate(Sum("airtime")).get('airtime__sum', 0)
        return t_sec / 3600
    
    def get_flights_total(self):
        return Flight.objects.count()
    
    def get_flights_for_year(self,year):
        """Return number of flights, 0 if no flights in year"""
        q = Flight.objects.filter(takeoff__datetime__year=year)
        return q.count()
    
    def get_only_xc(self):
        """Derive a boolean whether the flight is a local flight, or XC"""
        # todo: once we have xc distance from igc-xc-score, use instad
        # of points
        q = Flight.objects.annotate(
            xc_km_per_hour=ExpressionWrapper(
                F('xcscore__distance') / ( F('airtime') / 3600),
                output_field=FloatField()))
        # todo: threshold should be a setting, perhaps user-tunable?
        q = q.filter(xc_km_per_hour__gt=15)
        # exclude short straight flights
        q = q.filter(xcscore__distance__gt=10)
        return q

# Create your models here.
class Flight(JSONModel):
    """Root model"""
    # custom manager
    objects = FlightManager()
    
    # SHA256 - field throws error if hash already exists
    hash = models.CharField(max_length=64, unique=True)

    # date from igc file header
    date = models.DateField()

    # flight import datetime
    import_datetime = models.DateTimeField(auto_now_add=True)
    
    #  "airtime": {
    #    "value": 24275.0,
    #    "unit": "s"
    #  }
    # DurationField is a bad idea, since it breaks computations
    airtime = models.FloatField()

    # "glider_type": "OZONE Alpina 4"
    glider = models.CharField(max_length=255)


    @property
    def airtime_str(self):
        """format self.airtime into hh:mm:ss"""
        return str(timedelta(seconds=self.airtime))

    @property
    def to_geojson_feature_point(self):
        if not self.takeoff:
            return {}
        popup = f"<ul>\
            <li>{self.takeoff.datetime.date()}</li>\
            <li>{self.airtime_str} h</li>\
            <li>{self.xcscore.scoringName} {self.xcscore.score} p</li>\
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
        if self.hash:
            return self.hash[:6]
        return ""

    def _a_href(self,link_text):
        """Return a html link element to this flights detail page"""
        return f'<a href=" \
            {reverse('frontend:flight_detail', args=[self.id])}"> \
            {link_text}</a>'

    def __str__(self):
        s = ''
        s += f" {self.takeoff}" if hasattr(self,"takeoff") else ""
        s += f" {self.xcscore}" if hasattr(self,"xcscore") else ""
        return s

class Recorder(JSONModel):
    """ igc flight recorder """
    parent = models.OneToOneField(Flight, on_delete=models.CASCADE)
    
    # "recorder": {
    #   "type": "Google Pixel 7a 14",
    type = models.CharField(max_length=128,null=True)
    #   "code": "XCT",
    code = models.CharField(max_length=128,null=True)
    #   "gnss": "",
    gnss = models.CharField(max_length=128,null=True)
    #   "press": "InvenSense 1",
    press = models.CharField(max_length=128,null=True)
    #   "firmware_v": "0.9.11.11",
    firmware_v = models.CharField(max_length=128,null=True)
    #   "hardware_v": ""
    hardware_v = models.CharField(max_length=128,null=True)
    # }

class XCScore(JSONModel):
    """ igc-xc-score info"""
    # belongs to flight
    parent = models.OneToOneField(Flight, on_delete=models.CASCADE)
    
    # GeoJSON data
    geojson = models.JSONField()
    
    #"legs": [
    #  {
    #    "name": "TP1 : TP2",
    #    "distance": "37.05",
    #    "earthDistance": "37.053"
    #  },
    #  {
    #    "name": "TP2 : TP3",
    #    "distance": "51.22",
    #    "earthDistance": "51.223"
    #  },
    #  {
    #    "name": "TP3 : TP1",
    #    "distance": "44.05",
    #    "earthDistance": "44.052"
    #  }
    #],
    legs = models.JSONField()

    # "solution" > "bestSolution": {
    # "optimal": true,
    score = models.BooleanField()
    # "scoringName": "Closed FAI Triangle",
    scoringName = models.CharField(max_length=64)
    # "score": 208.94,
    score = models.FloatField()
    # "distance": 132.32,
    distance = models.FloatField()
    # "multiplier": 1.6,
    multiplier = models.FloatField()
    # "closingDistance": 1.73,
    closingDistance = models.FloatField(null=True)
    # "penalty": 1.73,
    penalty = models.FloatField(null=True)
    # "potentialMaxScore": null
    potentialMaxScore = models.FloatField(null=True)

    def __str__(self):
        s = f"{self.distance:.1f} km {self.scoringName} "
        return s


class Takeoff(JSONModel):
    # belongs to flight
    parent = models.OneToOneField(Flight, on_delete=models.CASCADE)

    # "name": "Col d'Izoard"
    name = models.CharField(max_length=255)
    # "dist": {
    #   "value": 70.53027327496399,
    #   "unit": "m"
    # }
    dist = models.FloatField()
    # "time": {
    #   "value": "2024-08-05 09:33:15",
    #   "unit": "UTC"
    # }
    datetime = models.DateTimeField()
    
    # named takeoff location from takeoff database
    # "db_lat": 47.0676,  
    db_lat = models.FloatField()
    # "db_lon": 9.104089999999998
    db_lon = models.FloatField()
    
    # coordinates of takeoff from tracklog
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

    # takeoff coordinates geocode information
    # "city": "Luchsingen",
    city = models.CharField(max_length=64)
    # "state": "Glarus",
    state = models.CharField(max_length=64)
    # "county": "Glarus",
    county = models.CharField(max_length=64)
    # "country_code": "CH",
    country_code = models.CharField(max_length=2)
    # "country": "Switzerland"
    country = models.CharField(max_length=64)

    def __str__(self):
        s = f"{str(self.datetime.time())} {self.country_code.upper()} "
        s += f" {self.name}" if self.name else ""
        return s
    

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
    datetime = models.DateTimeField()
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
    # "circ_time_L": {
    #   "value": 15.233626869821046,
    #   "unit": "s"
    # },
    circ_time_L = models.FloatField()
    # "circ_time_R": {
    #   "value": 14.410545324654665,
    #   "unit": "s"
    # }
    circ_time_R = models.FloatField()

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
