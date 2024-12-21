from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# https://docs.djangoproject.com/en/5.1/ref/class-based-views/
from django.views import generic
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView


# project
from importer.models import *


class HomePageView(TemplateView):
    template_name = "frontend/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # get total values over all flights
        context["airtime_total"] = Flight.objects.get_airtime_total()
        context["flights_total"] = Flight.objects.get_flights_total()
        
        # get values per year
        airtime_per_year = {}
        flights_per_year = {}
        for year in Flight.objects.get_unique_years():
            airtime_per_year[year] = Flight.objects.get_airtime_for_year(year)
            flights_per_year[year] = Flight.objects.get_flights_for_year(year)


        context["airtime_per_year"] = airtime_per_year
        context["flights_per_year"] = flights_per_year
        # for defining what 100% is in a bar view
        context["airtime_per_year_max"] = max(airtime_per_year.values())
        context["flights_per_year_max"] = max(flights_per_year.values())

        return context


class FlightListMap(TemplateView):
    """A map where each flight is represented as marker"""
    template_name = "frontend/flights_map.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latLon"] = \
            [f.to_geojson_feature_point for f in Flight.objects.all()]
        return context


class FlightListView(ListView):
    """A table where each flight is a row"""
    model = Flight
    paginate_by = 20
    template_name = "frontend/flights_list.html"
    context_object_name = 'flights'

    def get_queryset(self):
        # Apply ordering to the queryset to prevent UnorderedObjectListWarning
        return Flight.objects.order_by('id')


class FlightDetail(generic.DetailView):
    """Detail view of one flight, includes map and textual data"""
    model = Flight
    template_name = "frontend/flight_detail.html"