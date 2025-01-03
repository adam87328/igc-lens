from django.db import models
from django.db import IntegrityError

from .models import *
from . import util
from .microservice import MicroserviceInterface
from timezonefinder import TimezoneFinder
import pytz

class CreateFlight():

    def main(self,igc_StringIO):
        """Build flight models using elementary methods of this class"""
        flight = self.init_models()
        self.assign_igc(flight,igc_StringIO)
        self.assign_xcmetrics(flight,igc_StringIO)
        self.assign_xcscore(flight,igc_StringIO)
        lat = flight.takeoff.lat
        lon = flight.takeoff.lon
        self.assign_geocode(flight,lat,lon)
        self.assign_takeoffdb(flight,lat,lon)
        self.dependent_variables(flight)
        self.save_models(flight)
        return flight

    @staticmethod
    def init_models():
        """ Create empty root and child objects """
        f = Flight()
        Takeoff(parent=f)
        Landing(parent=f)
        Thermals(parent=f)
        Glides(parent=f)
        XCScore(parent=f)
        Recorder(parent=f)
        return f
    
    @staticmethod
    def save_models(flight):
        """ Save root and child objects to database """
        # save root
        try:
            flight.save()
        except IntegrityError as e:
            if 'UNIQUE constraint failed: importer_flight.hash' in str(e):
                msg = f'Flight already in database {flight.hash[:12]}'
                raise IntegrityError(msg)
            else:
                raise e
        # save children
        try:
            flight.takeoff.save()
            flight.landing.save()
            flight.thermals.save()
            flight.glides.save()
            flight.xcscore.save()
            flight.recorder.save()
        except Exception as e:
            flight.delete()
            raise e

    @staticmethod
    def assign_igc(flight,igc_StringIO):
        """ Assign igc file, compute hash """
        # compute hash
        flight.hash = util.compute_file_hash(igc_StringIO)
        # save file to disk
        # TODO file storage backend

    @staticmethod
    def assign_xcmetrics(flight,igc_StringIO):
        """  """
        msi = MicroserviceInterface()
        json_data = msi.xcmetrics_service(igc_StringIO)
        # unpack json data into one-to-one properties
        flight._assign_props_from_json(         json_data["info"]["flight"])
        flight.takeoff._assign_props_from_json( json_data["info"]["takeoff"])
        flight.landing._assign_props_from_json( json_data["info"]["landing"])
        flight.thermals._assign_props_from_json(json_data["info"]["thermals"])
        flight.glides._assign_props_from_json(  json_data["info"]["glides"])
        flight.recorder._assign_props_from_json(json_data["info"]["recorder"])
        # set remaining properties manually
        flight.glides.geojson =                 json_data["glides"]
        flight.thermals.geojson =               json_data["thermals"]
        flight.timeseries =                     json_data["timeseries"]
        # timezone
        flight.timezone = TimezoneFinder().timezone_at(
            lat=flight.takeoff.lat,
            lng=flight.takeoff.lon)

    @staticmethod
    def assign_xcscore(flight,igc_StringIO):
        msi = MicroserviceInterface()
        json_data = msi.xcscore_service(igc_StringIO)
        # unpack json data into one-to-one properties
        flight.xcscore._assign_props_from_json(json_data["solution"]["bestSolution"])
        # for 'legs'
        flight.xcscore._assign_props_from_json(json_data["solution"])
        # set remaining properties manually
        flight.xcscore.geojson = json_data["geojson"]

    @staticmethod
    def assign_geocode(flight,lat,lon):
        """ takeoff lat/lon """
        msi = MicroserviceInterface()
        json_data = msi.geocode_service(lat,lon)
        # unpack json data into one-to-one properties
        flight.takeoff._assign_props_from_json(json_data)

    @staticmethod
    def assign_takeoffdb(flight,lat,lon):
        """ takeoff lat/lon """
        msi = MicroserviceInterface()
        json_data = msi.takeoffdb_service(lat,lon)
        # unpack json data into one-to-one properties
        flight.takeoff._assign_props_from_json(json_data)

    @staticmethod
    def dependent_variables(flight):
        """Computations which depend on multiple sources"""
        flight.xcscore.xc_speed_airtime = \
            flight.xcscore.distance / (flight.airtime / 3600) # km/h
        # generate and save idstr
        flight.takeoff.idstr = flight.takeoff._make_idstr()