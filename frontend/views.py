from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from importer.models import *
from django.views import generic
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

# https://docs.djangoproject.com/en/5.1/ref/class-based-views/

class HomePageView(TemplateView):
    template_name = "frontend/home.html"


class FlightListMap(ListView):
    model = Flight
    template_name = "frontend/flights_map.html"
    context_object_name = 'flights'


class FlightListView(ListView):
    model = Flight
    paginate_by = 20
    template_name = "frontend/flights_list.html"
    context_object_name = 'flights'

    def get_queryset(self):
        # Apply ordering to the queryset to prevent UnorderedObjectListWarning
        return Flight.objects.order_by('id')


class FlightDetail(generic.DetailView):
    model = Flight
    template_name = "frontend/flight_detail.html"