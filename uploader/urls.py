from django.urls import path
from . import views
from .views import upload_file

urlpatterns = [
    path('', views.upload_file, name='home'),  # This makes upload the default page
    path('upload/', views.upload_file, name='upload_file'),
    path('upload/success/', views.upload_success, name='upload_success'),
]