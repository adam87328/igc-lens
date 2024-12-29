from django.test import TestCase
from django.core.files import File

import json

from .models import *
from .microservice import MicroserviceInterface
 
# class TestModels(TestCase):
# 
#     def setUp(self):
#         # need to have running microservices for this
#         msi = MicroserviceInterface()
#         if not msi.are_services_up():
#             self.skipTest()
#         
#         with open("./importer/testdata/valid_xctrack.igc") as f:
#             Flight.objects.create().init_from_file(File(f))
# 
#     def testToStr(self):
#         print("------- test_model_str -------")
#         print(Flight.objects.get().__str__())
#         print(Takeoff.objects.get().__str__())
#         print(Landing.objects.get().__str__())
#         print(Thermals.objects.get().__str__())
#         print(Glides.objects.get().__str__())