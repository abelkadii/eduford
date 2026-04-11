from geopy.distance import geodesic
from django.shortcuts import render, redirect
from .models import Location
from django.http import JsonResponse, HttpResponse
import json
from eduford import settings
import requests
from authentication.models import CustomUser
# Create your views here.



def index(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect('authentication:verify')
    else:
        return redirect('authentication:signin')
    location = Location.objects.filter(user=request.user)
    obj = {}
    if location:
        location = location[0]
        obj['lat'] = location.lat
        obj['lng'] = location.lng
        obj['country'] = location.country
        obj['address'] = location.address

    context = {
        'locatiion': obj,
        'location': 'study',
        'abbreviatedname': (request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...') if request.user.is_authenticated and request.user.email_verified else "",
    }
    return render(request, 'study/index.html', context)

def create(request):
    location = Location.objects.filter(user=request.user)
    if location:
        return HttpResponse('User Location Already exsists', status=401)
    
    return HttpResponse(status=200)

def search(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return HttpResponse('verify your account', status=400)
    else:
        return HttpResponse('login to your account or create a new account', status=400)
    body = json.loads(request.body)
    location = Location.objects.filter(user=request.user)
    distance = body['distance']
    if location and not distance:
        return HttpResponse(status=400)
    address = body['address']
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + settings.GOOGLE_MAPS_API_KEY;
    response = requests.get(url)
    if response.status_code != 200:
        return HttpResponse('Error Searching Google Maps', status=response.status_code)
    data = response.json()
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    country = [adcp['long_name'] for adcp in data['results'][0]['address_components'] if 'country' in adcp['types']]
    country = country[0] if country else data['results'][0]['formatted_address']
    if not location:
        location = Location(user = request.user, lat=lat, lng=lng, country=country, address=body['address'])
        location.save()
    else:
        location = location[0]
    # locations = Location.objects.exclude(id=location.id)
    locations = Location.objects.all()
    _distance = lambda l1, l2: geodesic((l1.lat, l1.lng), (l2.lat, l2.lng)).meters
    _filter = lambda l: _distance(l, location)<=distance*1000
    _within_locations = [i for i in locations if _filter(i)]
    serialized_locations = []
    for location in _within_locations:
        slc = {
            'lat': location.lat,
            'lng': location.lng,
            'country': location.country,
            'address': location.address,
            'name': location.user.first_name + ' ' + location.user.last_name,
            'email': location.user.email
        }
        serialized_locations.append(slc)
    return JsonResponse(serialized_locations, safe=False)

def load_map(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return HttpResponse('verify your account', status=400)
    else:
        return HttpResponse('login to your account or create a new account', status=400)
    url = "https://maps.googleapis.com/maps/api/js?libraries=geometry&key={}&callback=createSearchableMap".format(settings.GOOGLE_MAPS_API_KEY)
    response = requests.get(url)
    if response.status_code == 200:
        # Return the JavaScript file to the client
        return HttpResponse(response.content, content_type='application/javascript')
    else:
        # Handle error
        return HttpResponse('Error loading Google Maps API', status=response.status_code)