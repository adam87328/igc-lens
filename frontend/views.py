from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from importer.models import *
from django.views import generic
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

# https://docs.djangoproject.com/en/5.1/ref/class-based-views/

class HomePageView(TemplateView):
    template_name = "frontend/home.html"


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