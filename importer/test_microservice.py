from django.test import TestCase
from django.core.files import File

import requests
import json
from pathlib import Path

from .microservice import MicroserviceInterface

class TestMicroservice(TestCase):

    @classmethod
    def setUpClass(self):
        p = Path(__file__).resolve()
        # .igc files for testing
        self.td = p.parents[0] / 'testdata'

    @classmethod
    def tearDownClass(self):
        pass

    def testServicesUp(self):
        msi = MicroserviceInterface()
        self.assertTrue(msi.are_services_up())

    def testNearestTownService(self):
        msi = MicroserviceInterface()
        d = msi.nearest_town_service(47.0,9.0)
        self.assertEqual(d['city'],'Luchsingen')
        # with open(self.td / 'nearest_town.json','w') as f:
        #     json.dump(d, f, indent=2)

    def testAdmin1Service(self):
        msi = MicroserviceInterface()
        d = msi.admin1_service(47.0,9.0)
        self.assertEqual(d['admin0'],'Switzerland')
        self.assertEqual(d['admin1'],'Glarus')
        # with open(self.td / 'admin1.json','w') as f:
        #     json.dump(d, f, indent=2)

    def testTakeoffdbService(self):
        msi = MicroserviceInterface()
        d = msi.takeoffdb_service(47.0676, 9.10409)
        self.assertEqual(d['name'],'Fronalp')
        # with open(self.td / 'takeoffdb.json','w') as f:
        #     json.dump(d, f, indent=2)

    def testXcMetricsService(self):
        msi = MicroserviceInterface()
        with open(self.td / 'valid_xctrack.igc','r') as f:
            d = msi.xcmetrics_service(File(f))
        self.assertAlmostEqual(
            d['info']['flight']['airtime']['value'],
            24275) # seconds
        # with open(self.td / 'xcmetrics.json','w') as f:
        #     json.dump(d, f, indent=2)

    def testXcScoreService(self):
        msi = MicroserviceInterface()
        with open(self.td / 'valid_xctrack.igc','r') as f:
            d = msi.xcscore_service(File(f))
        self.assertAlmostEqual(
            d["solution"]['bestSolution']['distance'], 
            132.32) # km
        # with open(self.td / 'xcscore.json','w') as f:
        #     json.dump(d, f, indent=2)