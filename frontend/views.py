from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from importer.models import *
from django.views import generic


def home(request):
    return HttpResponse("home")

def flight_list(request):
    fl = Flight.objects.order_by("-import_datetime")[:20]
    context = {"fl": fl}
    return render(request, "frontend/flight_list.html", context)

#def flight_detail(request, flight_id):
#    flight = get_object_or_404(Flight, pk=flight_id)
#    return render(request, "frontend/flight_detail.html", {"flight": flight})
    
class FlightDetail(generic.DetailView):
    model = Flight
    template_name = "frontend/flight_detail.html"