from django.urls import path
from . import views

app_name = "frontend"
urlpatterns = [
    path('home/', views.home, name='home'),
    path('flight/list/', views.flight_list, name='flight_list'),
    path("flight/<int:pk>/", views.FlightDetail.as_view(), name="flight_detail"),
]