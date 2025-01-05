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
        
        # catch empty flight db
        if not fm.count():
            return {}
        
        # get total values over all flights
        total = {}
        total["flights"] = fm.all().count()
        total["airtime"] = fm.all().get_airtime()
        total["xc_km"] = fm.all().get_xckm()
        total["takeoffs"] = len(fm.all().get_unique_takeoffs())
        total["states"] = len(fm.all().get_unique_states())
        total["countries"] = len(fm.all().get_unique_countries())
        
        per_year = {}
        for y in fm.all().get_unique_years():
            qy = fm.all().filt_year(y)
            per_year[y] = {"airtime": {"abs": 0, "rel": 0},
                           "flights": {"abs": 0, "rel": 0},
                           "xc_km": {"abs": 0, "rel": 0},
                           "states":  {"abs": 0, "rel": 0},}
            per_year[y]["airtime"]["abs"] = qy.get_airtime()
            per_year[y]["flights"]["abs"] = qy.count()
            per_year[y]["xc_km"]["abs"] = qy.get_xckm()
            per_year[y]["states"]["abs"] = len(qy.get_unique_states())
        # compute values relative to best year
        for field in ["airtime", "flights","xc_km","states"]:
            m = max(item[field]["abs"] for item in per_year.values())
            for item in per_year.values():
                # in percent for use in CSS
                item[field]["rel"] = 100 * item[field]["abs"] / m

        per_takeoff = {}
        for y in fm.all().get_unique_takeoffs():
            qy = fm.all().filt_takeoff(y)
            per_takeoff[y] = {"airtime": 0,"flights": 0,"xc_km": 0}
            per_takeoff[y]["airtime"] = qy.get_airtime()
            per_takeoff[y]["flights"] = qy.count()
            per_takeoff[y]["xc_km"] = qy.get_xckm()
        # Sort the dictionary by the 'airtime' value of the inner dictionaries
        per_takeoff = dict(sorted(per_takeoff.items(), 
                                  key=lambda item: item[1]['airtime'],
                                  reverse=True)) # descending

        per_state = {}
        for y in fm.all().get_unique_states():
            qy = fm.all().filt_state(y)
            per_state[y] = {"airtime": 0,"flights": 0,"xc_km": 0}
            per_state[y]["airtime"] = qy.get_airtime()
            per_state[y]["flights"] = qy.count()
            per_state[y]["xc_km"] = qy.get_xckm()
        # Sort the dictionary by the 'airtime' value of the inner dictionaries
        per_state = dict(sorted(per_state.items(), 
                                key=lambda item: item[1]['airtime'],
                                reverse=True)) # descending

        context["per_year"] = per_year
        context["per_takeoff"] = per_takeoff
        context["per_state"] = per_state
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
        # takeoff 
        o = self.object.takeoff
        if o.name: # database match
            context["takeoff"] = f"{o.name}"
        else:
            context["takeoff"] = f"{o.idstr} (not in DB)"
        
        return context
    

class FlightListView(ListView):
    """A table where each flight is a row"""
    model = Flight
    context_object_name = 'flights'

    def get_queryset(self):
        qs = super().get_queryset()
        for value, filter in FlightFilter.objects.get().active.items():
            
            if filter == 'takeoff':
                qs = qs.filt_takeoff(value)

            if filter == 'xc_dist':
                # extract number
                match = re.search(r'\d+', value)
                qs = qs.filter(xcscore__distance__gt=int(match.group()))

            if filter == 'airtime':
                match = re.search(r'\d+', value)
                sec = 3600*int(match.group()) # hours to sec
                qs = qs.filter(airtime__gt=sec)

            if filter == 'scoring_name':
                qs = qs.filter(xcscore__scoringName=value)

        # todo: order-by via table headings
        return qs.order_by('-date')

    def get(self, request, *args, **kwargs):
        # accumulate filters in FlightFilter model
        if 'flightFilter' in request.GET:
            filter_verbose_name = request.GET.get('flightFilter')
            FlightFilter.objects.get().set_filter(filter_verbose_name)
        # reset FlightFilter model
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
    paginate_by = 50 # todo: setting

    #def get_context_data(self, **kwargs):
    #    context = super().get_context_data(**kwargs)
    #    rows = context['object_list']  # Your rows data
    #    # Loop through your rows and assign icons based on marker type
    #    for row in rows:
    #        # add fields to row
    #    return context

class FlightMapView(FlightListView):
    """A map where each flight is represented as marker"""
    template_name = "frontend/flights_map.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        # icon at takeoff location
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