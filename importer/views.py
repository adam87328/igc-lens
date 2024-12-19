import requests
import zipfile
import os
import io

from django.core.files import File
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse

from .forms import FileUploadForm
from .models import *

def index(request):
    return HttpResponse("hola!")

def upload_file(request):
    """IGC upload handler, accepts

    - single igc file
    - zip archive with igc files
    """
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
        try:
            if uploaded_file.name.lower().endswith('.igc'):
                messages.info(request, f'{uploaded_file.name}')
                spawn_flight(request,uploaded_file)

            elif uploaded_file.name.lower().endswith('.zip'):
                zip_file_iterate(uploaded_file,request)

            else:
                raise Exception(f'Unsupported file type, upload .igc or .zip')

        except Exception as e:
            messages.error(request, f'Error {e}')

        # return HttpResponseRedirect(reverse("frontend:flight_list"))
    else:
        # show upload form
        form = FileUploadForm()

    return render(request, 'upload.html', {'form': form})


def zip_file_iterate(zip_file,request):
    # Use the in-memory zip_file directly with zipfile.ZipFile
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # Iterate over the files in the zip
        for file_name in zip_ref.namelist():
            
            # Ensure the file has a .igc extension
            if not file_name.lower().endswith('.igc'):
                # Skip non-.igc files
                messages.info(request, f'{file_name} Skipping non-IGC')
                continue
            
            # ensure ascii file
            with zip_ref.open(file_name) as file:    
                try:
                    file_data = file.read().decode('ascii')
                except UnicodeDecodeError:
                    messages.info(request, f'{file_name} Skipping non-ASCII file')
                    continue
            
            # make a file-like object from asii file_data
            tmp = io.StringIO()
            tmp.write(file_data)
            # Wrap it in a Django File object
            messages.info(request, f'{file_name}')
            spawn_flight(request,File(tmp,name=file_name))

def spawn_flight(request,file):
    try:
        flight = Flight.objects.create()
        flight.init_from_file(file)
        messages.info(request, f'Ok {flight.__str__()}')
    except Exception as e:
        flight.delete()
        messages.info(request, f'Exception {e.__str__()}')