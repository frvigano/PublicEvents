#more examples availabile 
#https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/python-tutorial
#https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/quickstarts/python-labeled-data#analyze-forms-for-key-value-pairs-and-tables


#before executing install the custom vision SDK
#pip install azure-cognitiveservices-vision-customvision

#import some libraries
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
import json
import time
from requests import get, post

#map form recognizer models onto custom vision classes
models = {
    "BrianzAcque" : "0066c46b-d3d0-4637-bc8d-1b2ed21809b5",
    "EnelEnergia" : "70f310aa-6141-4fea-8e6c-d4b9f950b147",
    "EnelGas" : "69b3fd21-1440-4144-b287-77361ffc30ca"
}

# parameters to asynch call (form recognizer)
n_tries = 15
n_try = 0
wait_sec = 5
max_wait_sec = 60

#custom vision parameters
prediction_key =""
endpoint = "https://southcentralus.api.cognitive.microsoft.com/"
project_id ="7fbb04b5-8718-4338-82ed-03ba8b0fae7a"
publish_iteration_name ="Bollette"

#form recognizer parametes
endpointform = "https://formrecognizerfvi2.cognitiveservices.azure.com/"
apim_key = ""


# some image to test the pipeline
#image_file ="C:\\Users\\frvigano\\OneDrive - Microsoft\\Form Recognizer\\BrianzAcque\\acqua 01.jpg"
image_file ="C:\\Users\\frvigano\\OneDrive - Microsoft\\Form Recognizer\\EnelEnergia\\ENEL LUCE Fattura_002999999_13112018_2_M-page-001.jpg"

#create custom vision endpoint
predictor = CustomVisionPredictionClient(prediction_key, endpoint=endpoint)

#try to predict the class and the probability
with open(image_file, "rb") as image_contents:
    results = predictor.classify_image(project_id, publish_iteration_name, image_contents.read())
    documenttype = results.predictions[0].tag_name
    probability  = results.predictions[0].probability

# if we are confident, we apply the form recognizer model 
if probability > 0.8 :
    print("{} with probability {}".format(documenttype, probability))
    # call form recognizer model    
    with open(image_file, "rb") as image_contents:
        # models[documenttype] call the proper model id 
        post_url = endpointform + "/formrecognizer/v2.0-preview/custom/models/%s/analyze" % models[documenttype]
        
        # some call parameters and headers to make the http call 
        params = {
            "includeTextDetails": False
        }
        headers = {
            # Request headers
            'Content-Type': 'image/jpeg', # type can be application/pdf, image/jpeg, image/png, image/tiff
            'Ocp-Apim-Subscription-Key': apim_key
        }
        # call the form recognizer service to start analyzing the image
        resp = post(url = post_url, data = image_contents.read(), headers = headers, params = params)
        if resp.status_code != 202:
            print("POST analyze failed:\n%s" % json.dumps(resp.json()))
            quit()
        print("POST analyze succeeded:\n%s" % resp.headers)
        # get the URL to call and check results of the operation
        get_url = resp.headers["operation-location"]

        #try as many times as allowed. 
        while n_try < n_tries:
            resp = get(url = get_url, headers = {"Ocp-Apim-Subscription-Key": apim_key})
            resp_json = resp.json()
            if resp.status_code != 200:
                print("GET analyze results failed:\n%s" % json.dumps(resp_json))
                break
            status = resp_json["status"]
            # is succeeded print the fields (or do what you need to)
            if status == "succeeded":
#               print("Analysis succeeded:\n%s" % json.dumps(resp_json))
                fields = resp_json["analyzeResult"]["documentResults"][0]["fields"]
                for field in fields:
                    print ("{}:{}".format(field,fields[field]["valueString"]))
                break
            #if operation fails ... 
            if  status == "failed":
                print("Analysis failed:\n%s" % json.dumps(resp_json))
                break
            # Analysis still running. Wait and retry.
            time.sleep(wait_sec)
            n_try += 1
            wait_sec = min(2*wait_sec, max_wait_sec)     
else :
    # not confident. Define what you need to do
    print("Manage case")


