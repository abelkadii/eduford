import joblib
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import json
import math
import Levenshtein
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from eduford.settings import BASE_DIR
from .models import Diagnosis
import random

from eduford import settings
from payment.checkout import create_checkout_page
from checkout_sdk.exception import CheckoutApiException, CheckoutArgumentException, CheckoutAuthorizationException

global response
global symptoms
global symsmapping

global rfmodel
rfmodel = joblib.load(BASE_DIR/"predictor/models/pred-dis.joblib")
all_symptoms = rfmodel.feature_names_in_

precaution_df = pd.read_csv(BASE_DIR/'predictor/models/disease_precaution.csv')
disease_description = pd.read_csv(BASE_DIR/'predictor/models/disease_description.csv')
# disease_description.
# hospital_data = pd.read_csv(BASE_DIR/"predictor/models/Hospital_Directory.csv")
med=pd.read_csv(BASE_DIR/"predictor/models/rec-med.csv")
doctype=pd.read_csv(BASE_DIR/"predictor/models/Doctor_Versus_Disease.csv",encoding='ISO-8859-1')


response=dict()
response1=dict()

def must_be_authenticated_and_verified(f):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentication:signin')
        if not request.user.email_verified:
            return redirect('authentication:verify')
        return f(request, *args, **kwargs)
    return wrapper


@must_be_authenticated_and_verified
def home(request):
    symptoms = []
    for symptom in all_symptoms:
        symptoms.append({'value': symptom, 'name': ' '.join([i[0].upper()+i[1:] for i in symptom.split('_')])})
    context = {
        'location': 'predictor',
        'abbreviatedname': (request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...') if request.user.is_authenticated and request.user.email_verified else "",
        'symptoms': symptoms
    }
    return render(request, 'predictor/index.html', context)





def diagnose(symptoms):
    symsmapping = create_symptom_mapping(symptoms, all_symptoms)
    probabilities = rfmodel.predict_proba([symsmapping])
    disease_probabilities = dict(zip(rfmodel.classes_, probabilities[0]))
    top_n = 2 # top_n can't be greater than the number of diseases in the model
    if top_n>len(rfmodel.classes_):
        print("!!!!!!!!!!!!!!!!!! top_n can't be greater than the number of diseases in the model !!!!!!!!!!!!!!!!!!!")
    top_n = max(top_n, len(rfmodel.classes_))
    sorted_probabilities = sorted(disease_probabilities.items(), key=lambda x: x[1], reverse=True)[:top_n]
    response2 = []
    for disease, probability in sorted_probabilities:
        if probability>0:
            predicted_disease_precautions = precaution_df[precaution_df['Disease'] == disease]
            prec = []
            if not predicted_disease_precautions.empty:
                for column in ['Symptom_precaution_0', 'Symptom_precaution_1', 'Symptom_precaution_2', 'Symptom_precaution_3']:
                    precaution_value = predicted_disease_precautions[column].values[0]
                    precaution_value = None if isinstance(precaution_value, float) and math.isnan(precaution_value) else precaution_value
                    prec.append(precaution_value)

            try:
                result = doctype.loc[doctype['Disease'] == disease, 'Doctor']
                doc_type = result.values[0]
            except: doc_type="Doctor"
            desc = description.get(disease, disease)
            sd = disease_description[disease_description['Disease']==disease]
            if not sd.empty:
                desc=sd[disease_description.columns[-1]].values[0]
            else:
                desc = "description not available for {}".format(disease)

            disease_details = {
                'disease': disease,
                'description': desc,
                'probability': int(probability * 100),
                'precautions': prec,
                'doc_type': doc_type
            }
            
            response2.append(disease_details)
    return response2

# response1=dict()
response2 = []
response3=dict()

@must_be_authenticated_and_verified
def send_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        symptoms = data.get('symptoms')
        name = data.get('Name')
        age = data.get('Age')
        weight = data.get('Weight')
        height = data.get('Height')
        gender = data.get('Gender')
        cigar = data.get('Cigar')
        alcohol = data.get('Alcohol')
        pregnant = data.get('Pregnant')
        trimister = data.get('trimister')
        response2 = diagnose(symptoms)
        uuid = ''.join([random.choice('0123456789abcdef') for i in range(32)])
        diagnosis = Diagnosis(symptoms=json.dumps(symptoms), name=name, age=age, weight=weight, height=height, gender=gender, cigar=cigar, alcohol=alcohol, pregnant=pregnant, trimister=trimister, uuid=uuid)
        diagnosis.save()
        # to_be_saved = [symptoms, Name, Age, Weight, Height, Gender, Cigar, Alcohol, Pregnant, trimister]
        # print(to_be_saved)
        return JsonResponse({
            'response': response2,
            'id': diagnosis.id
        }, safe=False)
    else:
        return JsonResponse({"error": "POST method required"})

@must_be_authenticated_and_verified
def getReport(request, id):
    diagnose = Diagnosis.objects.filter(id=id)
    if not diagnose:
        return JsonResponse({'success': False, 'message': "404, not found"})
    uuid = diagnose[0].uuid
    try:
        response = create_checkout_page(settings.CHECKOUT_SECRET_KEY, settings.CHECKOUT_PRCESSING_CHANNEL_ID, [{"name": "Diagnosis Report", "quantity": 1, "price": 2999}], "Eduford", settings.WEBSITE_URL+"/predictor/report/{}".format(uuid), settings.WEBSITE_URL+"/?status=failure", settings.WEBSITE_URL+"/?status=cancel", f"REPORT", "KES", geocoder.ip({'127.0.0.1': 'me'}.get((ip:=request.META.get('REMOTE_ADDR')), ip)).geojson['features'][0]['properties']['country'], "en-US")
    except CheckoutApiException as err:
        print(err)
        return HttpResponse(status=500)
        
    except CheckoutArgumentException as err:
        print(err)
        return HttpResponse(status=501)

    except CheckoutAuthorizationException as err:
        print(err)
        return HttpResponse(status=502)
    return JsonResponse({"success": True, "redirect": response._links.redirect.href})
    

def report(request, uuid):
    dd = Diagnosis.objects.filter(uuid=uuid)
    if not dd:
        return JsonResponse({'success': False, 'message': "404, not found"})
    dd = dd[0]
    reponse = diagnose(json.loads(dd.symptoms))
    res = {
        'response': reponse,
        'symptoms': json.loads(dd.symptoms),
        'name': dd.name,
        'age': dd.age,
        'weight': dd.weight,
        'height': dd.height,
        'gender': dd.gender,
        'cigar': dd.cigar,
        'alcohol': dd.alcohol,
        'pregnant': dd.pregnant,
        'trimister': dd.trimister
    }
    return render(request, 'predictor/report.html', context={'res': json.dumps(res)})


@must_be_authenticated_and_verified
def update(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        gender = request.POST.get('gender')
        alcohol = request.POST.getlist('alcohol', ['X', 'N'])
        trisemister = request.POST.getlist('trisemister', ['A', 'B', 'C', 'D', 'N', 'X'])

        # Assuming `response` is a dictionary defined outside the view
        response = {'name': name, 'age': age, 'weight': weight, 'height': height, 'gender': gender, 'alcohol': alcohol, 'trisemister': trisemister}
        return JsonResponse(response)
    else:
        return JsonResponse({"error": "POST method required"})

@must_be_authenticated_and_verified
def locate(request):
    if request.method == 'POST':
        response1 = {}
        option = request.POST.get('locationOption')
        if option == "writtenLocation":
            userloc = request.POST.get('locationInput')
            t = getlatlong(userloc)
            latitude = t[0]
            longitude = t[1]
        else:
            latitude, longitude = get_live_location()

        hospitalcount = int(request.POST.get('hospitalRange', 3))
        response1.update({'latitude': latitude, 'longitude': longitude, 'hospitalcount': hospitalcount})

        # X = hospital_data[['lat', 'lon']].values
        X = 0
        global nbrs
        nbrs = NearestNeighbors(n_neighbors=hospitalcount, algorithm='ball_tree').fit(X)
        nearest_hospitals = suggest_nearest_hospitals(latitude, longitude)

        if nearest_hospitals:
            for c, hospital in enumerate(nearest_hospitals):
                response1.update({
                    f'hospital{c}': hospital[0],
                    f'distance{c}': hospital[1],
                    f'lat{c}': hospital[2],
                    f'long{c}': hospital[3]
                })
        return JsonResponse(response1)
    else:
        return JsonResponse({"error": "POST method required"})

@must_be_authenticated_and_verified
def medic(request):
    return JsonResponse(response2, safe=False)

@must_be_authenticated_and_verified
def displaymedic(request):
    if request.method == 'POST':
        response3 = {}
        syms = [input_string.replace('_', ' ') for input_string in symptoms]
        disease = request.POST.get('disease')
        probability = int(request.POST.get('probability'))
        age = int(response['age'])
        pregnancy_condition = response['trisemister']
        alcohol = response['alcohol']
        gender = response['gender']
        result = doctype.loc[doctype['Disease'] == disease, 'Doctor']
        doc_type = result.values[0]
        if age > 50:
            response3.update({"gotohospital": "urgent"})
        else:
            if probability < 50:
                medications = get_medication_info(syms)
                response3.update({"gotohospital": "for conformation", "medications": medications})
            else:
                medications = recmedicine(disease, age, gender, pregnancy_condition, alcohol)
                if medications:
                    response3.update({"medications": medications})
                else:
                    medications1 = get_medication_info([disease])
                    response3.update(medications1)
        response3.update({"disease": disease, "probability": probability, "doc_type": doc_type})
        return JsonResponse(response3)
    else:
        return JsonResponse({"error": "POST method required"})




















def get_medication_info(disease_list): #get medication using API
    medications_dict = {}
    base_url = "https://api.fda.gov/drug/label.json"
    for disease in disease_list:
        # Specify the query parameters for the API call
        params = {
            "search": f"indications_and_usage:{disease}",
            "limit": 5
        }
        try:
            # Send a GET request to the API endpoint
            response = requests.get(base_url, params=params)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()

                # Extract relevant information from the response
                medication_list = []
                for result in data['results']:
                    medication_name = result['openfda'].get('brand_name', None)
                    if medication_name and 'N/A' not in medication_name:  # Exclude 'N/A' values
                        medication_list.append(medication_name[0])

                medications_dict[disease] = medication_list
            else:
                 medications_dict[disease] = ["404-ERROR: connect to internet"]

        except requests.exceptions.RequestException as e:
            medications_dict[disease] = ["404-ERROR: connect to internet"]
    return medications_dict



description = json.load(open(BASE_DIR / "predictor/description.json"))
def find_nearest_condition(input_text, conditions_list):
    input_text = input_text.lower()
    best_match = None
    best_similarity = 0
    for condition in conditions_list:
        similarity = Levenshtein.ratio(input_text, condition.lower())
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = condition
    return best_match




def recmedicine(disease,age,gender,pregnancy_condition,alcohol):
    
    disease= find_nearest_condition(disease, [])
    # Filter the DataFrame based on the disease
    filtered_df = med[med['medical_condition'] == disease]
   

    if pregnancy_condition is not None:
        # Filter the DataFrame based on the allowed pregnancy categories
        filtered_df = filtered_df[filtered_df['pregnancy_category'].isin([pregnancy_condition])]
    
    if alcohol is not None:
        # Filter the DataFrame based on alcohol interaction
        filtered_df = filtered_df[filtered_df['alcohol'].isin([alcohol])]
        
    if int(age) < 10:
        # Filter dataset for users under 10 with at least 5 activity values
        filtered_df = filtered_df.nsmallest(5, 'activity')
        
    elif 10 <= int(age) <= 15:
        # Filter dataset for users between 10 and 15 with at least 10 activity values
        filtered_df = filtered_df.nsmallest(10, 'activity')
    
    
    # Get the "drug_name" column from the filtered DataFrame
    drug_names = filtered_df.head(5)['drug_name'].tolist()
    return drug_names




def create_symptom_mapping(symptoms_list, symptom_names):
    symptom_mapping = [1 if symptom in symptoms_list else 0 for symptom in symptom_names]
    return symptom_mapping


def suggest_nearest_hospitals(user_latitude, user_longitude):
    return 0
    # Find the indices of the nearest hospitals based on the user's location
    distances, indices = nbrs.kneighbors([[user_latitude, user_longitude]])
    
    nearest_hospitals = []
    for index in indices[0]:
        hospital_name = hospital_data.loc[index, "health_facility_name"]
        hospital_latitude = hospital_data.loc[index, "lat"]
        hospital_longitude = hospital_data.loc[index, "lon"]
        hospital_distance = calculate_road_distance(user_latitude,user_longitude, hospital_latitude, hospital_longitude)
        nearest_hospitals.append((hospital_name, hospital_distance, hospital_latitude, hospital_longitude))
    
    return nearest_hospitals


    
#calculate road distance between two locations

from geopy.distance import geodesic

def calculate_road_distance(lat1, lon1, lat2, lon2):
    # Coordinates of the two locations
    location1 = (lat1, lon1)
    location2 = (lat2, lon2)
    
    # Calculate the road distance between the two locations using geodesic distance
    distance = geodesic(location1, location2).kilometers
    
    return distance

#get lat long using location name

from geopy.geocoders import Nominatim
def getlatlong(location_str):
    # Create a Nominatim geocoder object
    geolocator = Nominatim(user_agent="http")

    # Use geocoder to convert location string to latitude and longitude
    location = geolocator.geocode(location_str)


    if location is not None:
        latitude = location.latitude
        longitude = location.longitude
        latitude=float(latitude)
        longitude=float(longitude)
    else:
        latitude,longitude=None,None
        
    return latitude,longitude

#get users current location

import geocoder

def get_live_location():
    g = geocoder.ip('me').geojson['features'][0]['properties']['country']

