# pip install --upgrade azure-cognitiveservices-vision-computervision

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
import sys
import time


subscription_key = ""
endpoint = ""


image = open("c:\\Temp\\1.pdf", "rb")

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Call API with URL and raw response (allows you to get the operation location)
recognize = computervision_client.read_in_stream (image, raw=True)

# Get the operation location (URL with an ID at the end) from the response
operation_location_remote = recognize.headers["Operation-Location"]
# Grab the ID from the URL
operation_id = operation_location_remote.split("/")[-1]

# Call the "GET" API and wait for it to retrieve the results 
while True:
    get_text_results = computervision_client.get_read_result(operation_id)
    if get_text_results.status not in ['NotStarted', 'Running']:
        break
    time.sleep(1)

# Print the detected text, line by line
if get_text_results.status == OperationStatusCodes.succeeded:
    for text_result in get_text_results.analyze_result.read_results:
        for line in text_result.lines:
            print(line.text)
            #print(line.bounding_box)
print()