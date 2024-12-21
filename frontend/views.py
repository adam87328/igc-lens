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
        # Flight object manager shortcut
        fm = Flight.objects

        # get total values over all flights
        total = {}
        total["flights"] = fm.get_flights_total()
        total["airtime"] = fm.get_airtime_total()
        
        # get values per year
        per_year = {}
        for y in fm.get_unique_years():
            per_year[y] = {"airtime": {"abs": 0, "rel": 0},
                           "flights": {"abs": 0, "rel": 0}}
            per_year[y]["airtime"]["abs"] = fm.get_airtime_for_year(y)
            per_year[y]["flights"]["abs"] = fm.get_flights_for_year(y)

        # compute values relative to best year
        for field in ["airtime", "flights"]:
            m = max(item[field]["abs"] for item in per_year.values())
            for item in per_year.values():
                # in percent for use in CSS
                item[field]["rel"] = 100 * item[field]["abs"] / m

        context["per_year"] = per_year
        context["total"] = total
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
        
        # Radio buttons: Get the 'filter' value from the GET request
        filter_value = self.request.GET.get('filter', 'all')
        # Apply filters based on the radio button value
        if filter_value == 'xc':
            queryset = Flight.objects.get_only_xc().order_by('id')
        else:
            queryset = Flight.objects.order_by('id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the current filter to the context so you can use it in the template
        context['current_filter'] = self.request.GET.get('filter', 'all')
        return context


class FlightDetail(generic.DetailView):
    """Detail view of one flight, includes map and textual data"""
    model = Flight
    template_name = "frontend/flight_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ensure correct booleans for JS, true vs True in python
        d = self.object.xcscore.geojson
        context["xcscore_layer"] = json.dumps(d)
        return context