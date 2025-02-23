from django.shortcuts import render, redirect
from .forms import UploadedFile, UploadedFileForm
from .models import UploadedFile

def upload_file(request):
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')
    else:
        form = UploadedFileForm()
    return render(request, 'uploader/upload.html', {'form': form})

def upload_success(request):
    return render(request, 'uploader/upload_success.html')

# Create your views here.
