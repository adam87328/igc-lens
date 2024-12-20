from django.urls import path
from . import views

app_name = "frontend"
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('flights/list/', views.FlightListView.as_view(), name='flights_list'),
    path('flights/map/', views.FlightListMap.as_view(), name='flights_map'),
    path("flight/<int:pk>/", views.FlightDetail.as_view(), name="flight_detail"),
]