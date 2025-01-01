from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# https://docs.djangoproject.com/en/5.1/ref/class-based-views/
from django.views import generic
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

import json
import re

# project
from importer.models import *
from frontend.models import *

class HomepageView(TemplateView):
    template_name = "frontend/homepage.html"


class StatisticsView(TemplateView):
    template_name = "frontend/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Flight object manager shortcut
        fm = Flight.objects        
        
        # empty flight db
        if not fm.count():
            return {}
        
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
    

class FlightDetailView(generic.DetailView):
    """Detail view of one flight, includes map and textual data"""
    model = Flight
    template_name = "frontend/flight_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ensure correct booleans for JS, true vs True in python
        d = self.object.xcscore.geojson
        context["xcscore_layer"] = json.dumps(d)
        # map bounding box
        lat = self.object.timeseries['lat']
        lon = self.object.timeseries['lon']
        context["corner_NE"] = [max(lat),max(lon)]
        context["corner_SW"] = [min(lat),min(lon)]
        return context
    

class FlightListView(ListView):
    """A table where each flight is a row"""
    model = Flight
    context_object_name = 'flights'

    def get_queryset(self):
        qs = super().get_queryset()
        for value, filter in FlightFilter.objects.get().active.items():

            if filter == 'xc_dist':
                # extract number
                match = re.search(r'\d+', value)
                qs = qs.filter(xcscore__distance__gt=int(match.group()))

            if filter == 'airtime':
                match = re.search(r'\d+', value)
                sec = 3600*int(match.group()) # hours to sec
                qs = qs.filter(airtime__gt=sec)

            if filter == 'takeoff':
                qs = qs.filter(takeoff__name=value)

            if filter == 'scoring_name':
                qs = qs.filter(xcscore__scoringName=value)

        # todo: order-by via table headings
        return qs.order_by('id')

    def get(self, request, *args, **kwargs):
        # Store the checkbox value in the session if submitted
        if 'flightFilter' in request.GET:
            filter_verbose_name = request.GET.get('flightFilter')
            FlightFilter.objects.get().set_filter(filter_verbose_name)

        if 'reset' in request.GET:
            o = FlightFilter.objects.get()
            o.active = {}
            o.save()

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # todo: get FlightFilter for current user
        filter = FlightFilter.objects.get()
        context['filter_all'] = list(filter.all)
        context['filter_active'] = list(filter.active)    
        return context


class FlightTableView(FlightListView):
    """A classic table"""
    template_name = "frontend/flights_table.html"
    paginate_by = 20

    def get_icon_for_marker_type(self, marker_type):
        icon_urls = {
            'Local Flight': 'icons/local_flight.svg',
            'Free Flight': 'icons/free_flight.svg',
            'Free Triangle': 'icons/flat_triangle.svg',
            'FAI Triangle': 'icons/fai_triangle.svg',
            'Closed Free Triangle': 'icons/closed_flat_triangle.svg',
            'Closed FAI Triangle': 'icons/closed_fai_triangle.svg'
        }
        return icon_urls.get(marker_type, None)  # None if no matching marker_type

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = context['object_list']  # Your rows data

        # Loop through your rows and assign icons based on marker type
        for row in rows:
            if row.xcscore.is_local():
                row.xcscore.scoringName = "Local Flight"
            row.icon_url = self.get_icon_for_marker_type(row.xcscore.scoringName)

        return context

class FlightMapView(FlightListView):
    """A map where each flight is represented as marker"""
    template_name = "frontend/flights_map.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        
        context["marker_list"] = [f.takeoff_marker() for f in qs]
        # map bounding box
        if qs:
            lat = qs.values_list('takeoff__lat', flat=True)
            lon = qs.values_list('takeoff__lon', flat=True)
            context["corner_NE"] = [max(lat),max(lon)]
            context["corner_SW"] = [min(lat),min(lon)]
        else:
            # ain't nothing to show
            context["corner_NE"] = [-48.875486, -123.392519]
            context["corner_SW"] = [-48.875486, -123.392519]

        return context