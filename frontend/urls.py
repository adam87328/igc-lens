from django.urls import path
from . import views

app_name = "frontend"
urlpatterns = [
    path('', views.HomepageView.as_view(), name='homepage'),
    path('flights/table/', views.FlightTableView.as_view(), name='flights_table'),
    path('flights/map/', views.FlightMapView.as_view(), name='flights_map'),
    path("flightdetail/<int:pk>/", views.FlightDetailView.as_view(), name="flight_detail"),
    path('stats/totals', views.StatisticsView.as_view(), name='totals'),
    path('stats/years', views.StatisticsView.as_view(), name='years'),
    path('stats/places', views.StatisticsView.as_view(), name='places'),
    path('stats/evolution', views.StatisticsView.as_view(), name='evolution'),
]