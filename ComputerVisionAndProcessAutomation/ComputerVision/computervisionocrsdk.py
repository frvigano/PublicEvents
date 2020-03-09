from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes

endpoint ="https://westeurope.api.cognitive.microsoft.com/"
subscription_key = ""
pathToFileInDisk = "c:\Temp\Invoice.png"

# object to call APIS
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

image = open(pathToFileInDisk, "rb")

#read api
recognize_printed_results = computervision_client.batch_read_file_in_stream(image, raw=True)

# Get the operation location (URL with an ID at the end) from the response
operation_location_remote = recognize_printed_results.headers["Operation-Location"]
# Grab the ID from the URL
operation_id = operation_location_remote.split("/")[-1]

# Call the "GET" API and wait for it to retrieve the results 
while True:
    get_printed_text_results = computervision_client.get_read_operation_result(operation_id)
    if get_printed_text_results.status not in ['NotStarted', 'Running']:
        break
    time.sleep(1)

# Print the detected text, line by line
if get_printed_text_results.status == TextOperationStatusCodes.succeeded:
    for text_result in get_printed_text_results.recognition_results:
        for line in text_result.lines:
            print(line.text)
            #print(line.bounding_box)
print()


image = open(pathToFileInDisk, "rb")

# OCR API with SDK
ocr_result_local = computervision_client.recognize_printed_text_in_stream(image, detect_orientation=True, raw=False, language='en')

type(ocr_result_local)

for region in ocr_result_local.regions:
    for line in region.lines:
#        print("Bounding box: {}".format(line.bounding_box))
        s = ""
        for word in line.words:
            s += word.text + " "
        print(s)
print()



