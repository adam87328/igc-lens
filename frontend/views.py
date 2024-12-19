from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from importer.models import *
from django.views import generic
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

# https://docs.djangoproject.com/en/5.1/ref/class-based-views/

class HomePageView(TemplateView):
    template_name = "frontend/home.html"

# def flight_list(request):
#     fl = Flight.objects.order_by("-import_datetime")[:20]
#     context = {"fl": fl}
#     return render(request, "frontend/flight_list.html", context)

class FlightListView(ListView):
    model = Flight
    paginate_by = 20
    template_name = "frontend/flight_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fl"] = Flight.objects.order_by("-import_datetime")
        return context

#def flight_detail(request, flight_id):
#    flight = get_object_or_404(Flight, pk=flight_id)
#    return render(request, "frontend/flight_detail.html", {"flight": flight})
    
class FlightDetail(generic.DetailView):
    model = Flight
    template_name = "frontend/flight_detail.html"