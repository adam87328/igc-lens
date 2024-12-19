from django.test import TestCase
from django.core.files import File

import json

from .models import *
from .microservice import MicroserviceInterface

class TestModelInit(TestCase):

    def setUp(self):
        # valid example output of xc-metrics microservice
        with open("./importer/testdata/xc_metrics_service_response.json", 'r') as file:
            self.d = json.load(file)
        
    def testCreateObjectsStandalone(self):
        # create objects manually
        flight = Flight.objects.create(file_hash="asdf")
        Takeoff.objects.create(
            parent=flight,
            json_data=self.d["info"]["takeoff"])
        Landing.objects.create(
            parent=flight,
            json_data=self.d["info"]["landing"])
        Thermals.objects.create(
            parent=flight,
            json_data=self.d["info"]["thermals"])
        Glides.objects.create(
            parent=flight,
            json_data=self.d["info"]["glides"])

    def testXcMetricsResponse(self):
        # use flight method to create children
        flight = Flight.objects.create(file_hash="qwertyu")
        flight._xc_metrics_response(self.d)
        self.assertTrue(hasattr(flight,"takeoff"))
        self.assertTrue(hasattr(flight,"landing"))
        self.assertTrue(hasattr(flight,"thermals"))
        self.assertTrue(hasattr(flight,"glides"))
        # fields not filled generically from json
        self.assertIsNotNone(flight.thermals.geojson)
        self.assertIsNotNone(flight.glides.geojson)

    def testCreateFromFile(self):
        # need to have running microservices for this
        msi = MicroserviceInterface()
        if not msi.are_services_up():
            self.skipTest("microservices down")
        
        with open("./importer/testdata/valid_xctrack.igc") as f:
            Flight.objects.create().init_from_file(File(f))
        
        flight = Flight.objects.get()
        self.assertTrue(hasattr(flight,"takeoff"))
        self.assertTrue(hasattr(flight,"landing"))
        self.assertTrue(hasattr(flight,"thermals"))
        self.assertTrue(hasattr(flight,"glides"))
        # fields not filled generically from json
        self.assertIsNotNone(flight.glides.geojson)
        self.assertIsNotNone(flight.thermals.geojson)
        
 
class TestModels(TestCase):

    def setUp(self):
        # need to have running microservices for this
        msi = MicroserviceInterface()
        if not msi.are_services_up():
            self.skipTest()
        
        with open("./importer/testdata/valid_xctrack.igc") as f:
            Flight.objects.create().init_from_file(File(f))

    def testToStr(self):
        print("------- test_model_str -------")
        print(Flight.objects.get().__str__())
        print(Takeoff.objects.get().__str__())
        print(Landing.objects.get().__str__())
        print(Thermals.objects.get().__str__())
        print(Glides.objects.get().__str__())

    def testValues(self):
        # Retrieve the model object
        o = Flight.objects.get()
        
        # Check if the object is created and has correct attributes
        self.assertEqual(o.airtime_str, "6:44:35")
        self.assertEqual(o.airtime, 24275.0)
       