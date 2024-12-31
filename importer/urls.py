from django.urls import path
from . import views

app_name = "importer"
urlpatterns = [
    path('upload/', views.FileUpload.as_view(), name='upload'),
]
