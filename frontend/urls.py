from django.urls import path
from . import views

app_name = "frontend"
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('flights/table/', views.FlightTableView.as_view(), name='flights_table'),
    path('flights/map/', views.FlightMapView.as_view(), name='flights_map'),
    path("flight/<int:pk>/", views.FlightDetail.as_view(), name="flight_detail"),
]