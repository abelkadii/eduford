from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from eduford.shop.models import Product
# Create your views here.

def views(request):
    if request.user.is_authenticated:
        return HttpResponse("Not Autherized (401)")
    if request.user.email_verified:
        return HttpResponse("Not Verified (401)")
    if request.method!="POST":
        return HttpResponse(400)
    payment_type = request.POST.get('type')
    if payment_type=='book':
        items = 'book'
    elif payment_type=='shop':
        items = request.POST.get('items')

    else:
        return HttpResponse(404)


    
    