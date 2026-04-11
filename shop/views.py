from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from  .models import Product, Order
from payment.checkout import create_checkout_page
from checkout_sdk.exception import CheckoutApiException, CheckoutArgumentException, CheckoutAuthorizationException
from eduford import settings
import random
import json
from django.contrib import messages

import geocoder

# Create your views here.

def random_string(n):
    return ''.join([random.choice("QWRTYUIOPASDFGHJKLZXCVBNM0123456789") for i in range(n)])
def index(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect('authentication:verify')
    else:
        return redirect('authentication:signin')
    context = {
        'location': 'shop',
        'abbreviatedname': request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...',
    }
    status = request.GET.get('status', None)
    if status == 'success':
        messages.success(request, "Yout Order has been placed")
    if status == 'failure':
        messages.success(request, "Your Order Was Canceld")
    if status == 'cancel':
        messages.success(request, "The Checkout Failed")
    return render(request, 'shop/index.html', context)

def get_products(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect('authentication:verify')
    else:
        return redirect('authentication:signin')
    products = Product.objects.all()
    serialized = [{
        "id":pr.id,
        "name":pr.name,
        "price":pr.price,
        "image":pr.image,
    } for pr in products]
    return JsonResponse(serialized, safe=False)

currencyMultipliers = {
    "USD": 1,
    "KES": 127.20,
}

def buy(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return HttpResponse('verify your account', status=400)
    else:
        return HttpResponse('login to your account or create a new account', status=400)
    if request.method != 'POST':
        return HttpResponse(status=400)
    
    # print(request.POST, request.body.products)
    # return
    _orders = json.loads(request.body)['products']
    _currency = json.loads(request.body)['currency']
    orders = []
    for order in _orders:
        product = Product.objects.filter(id=order['product_id'])
        if not product:
            return HttpResponse(status=404)
        order['product']=product[0]
        if order['quantity']>order['product'].stock:
            return HttpResponse(f'order quantity is greater than {order["product"].name} stock')
        orders.append(order)
    payment = []
    reg_orders = []
    for ord in orders:
        order = Order(user=request.user, product=ord['product'], quantity=ord['quantity'], price=ord['product'].price)
        payment.append({
            'name': ord['product'].name,
            'quantity': ord['quantity'],
            'price': ord['product'].price*currencyMultipliers.get(_currency, 1000000),
        })
        reg_orders.append(order)
    try:
        response = create_checkout_page(settings.CHECKOUT_SECRET_KEY, settings.CHECKOUT_PRCESSING_CHANNEL_ID, payment, "Eduford", settings.WEBSITE_URL+"/shop?status=success", settings.WEBSITE_URL+"/shop?status=failure", settings.WEBSITE_URL+"/shop?status=cancel", f"ORD-"+random_string(3), _currency, geocoder.ip({'127.0.0.1': 'me'}.get((ip:=request.META.get('REMOTE_ADDR')), ip)).geojson['features'][0]['properties']['country'], "en-US")
    except CheckoutApiException as err:
        print(err)
        return HttpResponse(status=500)
        
    except CheckoutArgumentException as err:
        print(err)
        return HttpResponse(status=501)

    except CheckoutAuthorizationException as err:
        print(err)
        return HttpResponse(status=502)
    for order in reg_orders:
        order.payement_id = response.id
        order.payement_reference = response.reference
        order.status = 'payment_created'
        order.save()
    return JsonResponse({"success": True, "redirect": response._links.redirect.href})
        
