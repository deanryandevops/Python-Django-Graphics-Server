import os
import logging
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UploadedFileForm
from .models import UploadedFile

# Jenkins configuration
JENKINS_URL = "http://51.186.164.197:8080/job/Unity-Pipeline"
JENKINS_USER = "deanryan"
JENKINS_TOKEN = "114470e34629f3f5b04caaac8f06f0294f"

# URL for uploading files to Jenkins machine (same as the curl command)
JENKINS_UPLOAD_URL = "http://51.186.164.197:8000/upload/"

# Set up logging
logger = logging.getLogger(__name__)


def upload_file(request):
    """
    Handles file upload, sends it to Jenkins machine, and triggers the pipeline.
    """
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the uploaded file locally (optional, for logging or backup)
                uploaded_file = form.save()
                file_name = uploaded_file.file.name
                file_path = uploaded_file.file.path

                # Log the file upload
                logger.info(f"File uploaded successfully: {file_name} at {file_path}")

                # Upload the file to the Jenkins machine (like the curl command)
                if upload_to_jenkins(file_path, file_name):
                    logger.info(f"File uploaded to Jenkins machine: {file_name}")

                    # Trigger Jenkins job with the file name as a parameter
                    if trigger_jenkins(file_name):
                        logger.info(f"Jenkins job triggered successfully for file: {file_name}")
                        return redirect('upload_success')
                    else:
                        logger.error(f"Failed to trigger Jenkins job for file: {file_name}")
                        return render(
                            request,
                            'uploader/upload.html',
                            {'form': form, 'error': 'Failed to trigger Jenkins job'}
                        )
                else:
                    logger.error(f"Failed to upload file to Jenkins machine: {file_name}")
                    return render(
                        request,
                        'uploader/upload.html',
                        {'form': form, 'error': 'Failed to upload file to Jenkins'}
                    )

            except Exception as e:
                # Log any unexpected errors
                logger.error(f"An error occurred during file upload or Jenkins triggering: {e}")
                return render(
                    request,
                    'uploader/upload.html',
                    {'form': form, 'error': 'An unexpected error occurred. Please try again.'}
                )

    else:
        form = UploadedFileForm()

    return render(request, 'uploader/upload.html', {'form': form})


def upload_success(request):
    """
    Displays a success page after a successful file upload and Jenkins job trigger.
    """
    return render(request, 'uploader/upload_success.html')


def upload_to_jenkins(file_path, file_name):
    """
    Uploads the file to the Jenkins machine using an HTTP POST request (like the curl command).

    Args:
        file_path (str): The local path of the file.
        file_name (str): The name of the file.

    Returns:
        bool: True if the file was uploaded successfully, False otherwise.
    """
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_name, file)}
            response = requests.post(JENKINS_UPLOAD_URL, files=files)

        if response.status_code == 200:
            logger.info(f"File uploaded to Jenkins machine successfully: {file_name}")
            return True
        else:
            logger.error(f"Failed to upload file to Jenkins machine: {response.status_code}, {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error uploading file to Jenkins machine: {e}")
        return False


def trigger_jenkins(file_name):
    """
    Triggers the Jenkins pipeline with the file name as a parameter.

    Args:
        file_name (str): The name of the uploaded file.

    Returns:
        bool: True if the Jenkins job was triggered successfully, False otherwise.
    """
    try:
        # Prepare the payload with the file name as a parameter
        payload = {'MODEL_NAME': file_name}

        # Make a POST request to trigger the Jenkins job
        response = requests.post(
            f"{JENKINS_URL}/buildWithParameters",  # Jenkins build URL with parameters
            auth=(JENKINS_USER, JENKINS_TOKEN),   # Jenkins user authentication
            data=payload                          # The data sent as part of the POST request (parameters)
        )

        # Check if the job was triggered successfully (status code 200 or 201)
        if response.status_code in [200, 201]:
            logger.info(f"Jenkins job triggered successfully for file: {file_name}")
            return True
        else:
            # Log the failure
            logger.error(f"Failed to trigger Jenkins job: {response.status_code}, {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        # Catch network or request-related errors
        logger.error(f"Network error while triggering Jenkins: {e}")
        return False

    except Exception as e:
        # Catch other unforeseen exceptions
        logger.error(f"An unexpected error occurred while triggering Jenkins: {e}")
        return False