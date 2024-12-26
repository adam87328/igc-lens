from django.test import TestCase
from django.core.files import File

from pathlib import Path
import json
import io

from .models import *
from .flight_create import CreateFlight as CF
from .microservice import MicroserviceInterface

class TestModelCreation(TestCase):

    @classmethod
    def setUpClass(self):
        p = Path(__file__).resolve()
        # .igc files for testing
        self.td = p.parents[0] / 'testdata'

    @classmethod
    def tearDownClass(self):
        pass

    def test_init_models(self):
        flight = CF.init_models()
        self.assertIsInstance(flight,Flight)

    def test_assign_igc(self):
        # file-like object in memory
        igc = io.StringIO()
        # copy contents from testfile
        with open(self.td / 'valid_xctrack.igc','r') as f:
            igc.write(f.read())
        # 
        flight1 = CF.init_models()
        CF.assign_igc(flight1,igc)
        self.assertIsNotNone(flight1.hash)
        # # Assign same igc file to second flight, which should not raise an 
        # # exception, since the flights have not been saved
        # flight2 = CF.init_models()
        # CF.assign_igc(flight2,igc)
        # # saveing first flight
        # flight1.save()
        # # as both flights have the same hash, saving the second flight should
        # # raise an exception:
        # # django.db.utils.IntegrityError: UNIQUE constraint failed: 
        # # importer_flight.hash
        # from django.db.utils import IntegrityError
        # self.assertRaises(IntegrityError,flight2.save)

    def test_assign_xcmetrics(self):
        # file-like object in memory
        igc = io.StringIO()
        # copy contents from testfile
        with open(self.td / 'valid_xctrack.igc','r') as f:
            igc.write(f.read())
        # 
        flight = CF.init_models()
        CF.assign_xcmetrics(flight,igc)
        
    def test_assign_xcscore(self):
        # file-like object in memory
        igc = io.StringIO()
        # copy contents from testfile
        with open(self.td / 'valid_xctrack.igc','r') as f:
            igc.write(f.read())
        # 
        flight = CF.init_models()
        CF.assign_xcscore(flight,igc)

    def test_assign_geocode(self):
        flight = CF.init_models()
        lat = 46.9664
        lon = 9.03715
        CF.assign_geocode(flight,lat,lon)

    def test_assign_geocode(self):
        flight = CF.init_models()
        lat = 47.0676
        lon = 9.10408
        CF.assign_geocode(flight,lat,lon)

    def test_create_flight(self):
        # file-like object in memory
        igc = io.StringIO()
        # copy contents from testfile
        with open(self.td / 'valid_xctrack.igc','r') as f:
            igc.write(f.read())

        cf = CF()
        cf.main(igc)