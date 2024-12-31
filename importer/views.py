import requests
import zipfile
import os
import io

from django.core.files import File
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.views import View

from .forms import FileUploadForm
from .models import *
from .flight_create import CreateFlight

from frontend.models import *

class FileUpload(View):
    """IGC upload handler, accepts

    - single igc file
    - zip archive with igc files
    """
    form_class = FileUploadForm
    template_name = 'importer/upload.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            messages.success(request, f'uploaded {uploaded_file.name}')

            if uploaded_file.name.lower().endswith('.igc'):
                # copy file content to StringIO object
                file_data = uploaded_file.read().decode('ascii')
                igc_StringIO = io.StringIO()
                igc_StringIO.write(file_data)
                self.spawn_flight(request,igc_StringIO,uploaded_file.name)

            elif uploaded_file.name.lower().endswith('.zip'):
                self.zip_file_iterate(uploaded_file,request)

            else:
                raise Exception(f'Unsupported file type, upload .igc or .zip')
            
            # update FlightFilter object for user
            # delete if exists
            o, *_ = FlightFilter.objects.get_or_create()
            o.delete()
            # new
            o = FlightFilter.objects.create()
            o.add_default()
            o.add_takeoffs()
            o.save()

            #return HttpResponseRedirect("/success/")
        return render(request, self.template_name, {"form": form})

    @staticmethod
    def zip_file_iterate(zip_file,request):
        # Use the in-memory zip_file directly with zipfile.ZipFile
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # Iterate over the files in the zip
            for file_name in zip_ref.namelist():
                
                # Ensure the file has a .igc extension
                if not file_name.lower().endswith('.igc'):
                    # Skip non-.igc files
                    messages.warning(request, f'{file_name} Skipping non-IGC')
                    continue
                
                # ensure ascii file
                with zip_ref.open(file_name) as file:    
                    try:
                        file_data = file.read().decode('ascii')
                    except UnicodeDecodeError:
                        messages.warning(request, 
                                        f'{file_name} Skipping non-ASCII file')
                        continue
                
                # make a file-like object from asii file_data
                igc_StringIO = io.StringIO()
                igc_StringIO.write(file_data)
                FileUpload.spawn_flight(request,igc_StringIO,file_name)
    
    @staticmethod
    def spawn_flight(request,igc_StringIO,file_name):
        cf = CreateFlight()
        try:
            flight = cf.main(igc_StringIO)
            messages.success(request, f'OK {file_name}: {flight.__str__()}')
            
        except Exception as e:
            messages.error(
                request, 
                f' {file_name} ({e.__str__()})')