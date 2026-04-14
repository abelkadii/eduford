import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Appointment
from payment.checkout import create_checkout_page, CheckoutConfigurationException
from checkout_sdk.exception import CheckoutApiException, CheckoutArgumentException, CheckoutAuthorizationException
from eduford import settings
from django.contrib import messages
import geocoder
# Create your views here.

logger = logging.getLogger(__name__)

def index(request):
    context = {"location": "home"}
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect("/verify?redirect=home")
        context['abbreviatedname'] = request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...'
        context["first_name"]= request.user.first_name
        context["last_name"]= request.user.last_name
        context["email"]= request.user.email
    else:
        context["first_name"] = ""
        context["last_name"] = ""
        context["email"] = ""
    status = request.GET.get('status', None)
    if status == 'success':
        messages.success(request, "Appointment Booked Successfuly")
    if status == 'failure':
        messages.success(request, "Appointment Booking Was Canceld")
    if status == 'cancel':
        messages.success(request, "The Checkout Failed")
    return render(request, "core/index.html", context)

def about(request):
    context = {"location": "about"}
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect("/verify?redirect=about")
        context['abbreviatedname'] = request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...'
        
    return render(request, "core/about.html", context)

def blog(request):
    context = {"location": "blog"}
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect("/verify?redirect=blog")
        context['abbreviatedname'] = request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...'
        
    return render(request, "core/blog.html", context)

def contact(request):
    context = {"location": "contact"}
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect("/verify?redirect=contact")
        context['abbreviatedname'] = request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...'
        
    return render(request, "core/contact.html", context)

def course(request):
    context = {"location": "course"}
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect("/verify?redirect=course")
        context['abbreviatedname'] = request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...'
        
    return render(request, "core/course.html", context)

def book(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return JsonResponse({'status': 'error', 'message': 'Verify your account first.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Log in to your account or create a new one.'}, status=400)

    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['laname']
        email = request.POST['email']
        phone = request.POST['phone']
        date = request.POST['date']
        time = request.POST['time']
        appointment = Appointment(user=request.user, first_name=fname, last_name=lname, email=email, phone=phone, date=date, time=time)
        try:
            response = create_checkout_page(settings.CHECKOUT_SECRET_KEY, settings.CHECKOUT_PRCESSING_CHANNEL_ID, [{"name": "Booking an appointment", "quantity": 1, "price": 1999}], "Eduford", settings.WEBSITE_URL+"/?status=success", settings.WEBSITE_URL+"/?status=failure", settings.WEBSITE_URL+"/?status=cancel", f"APP", "KES", geocoder.ip({'127.0.0.1': 'me'}.get((ip:=request.META.get('REMOTE_ADDR')), ip)).geojson['features'][0]['properties']['country'], "en-US")
        except CheckoutConfigurationException as err:
            logger.error("Checkout is misconfigured for appointment bookings: %s", err)
            return JsonResponse({'status': 'error', 'message': str(err)}, status=500)
        except CheckoutApiException as err:
            logger.exception("Checkout API error while creating an appointment checkout session.")
            return JsonResponse({'status': 'error', 'message': 'Unable to create the checkout session right now.'}, status=502)
             
        except CheckoutArgumentException as err:
            logger.exception("Invalid checkout request while creating an appointment checkout session.")
            return JsonResponse({'status': 'error', 'message': 'Unable to create the checkout session right now.'}, status=500)

        except CheckoutAuthorizationException as err:
            logger.exception("Checkout authorization failed while creating an appointment checkout session.")
            return JsonResponse({'status': 'error', 'message': 'Checkout credentials were rejected by the payment provider.'}, status=502)
        appointment.payement_id = response.id
        appointment.payement_reference = response.reference
        appointment.status = 'payment_created'
        appointment.save()
        return JsonResponse({"status": "success", "redirect": response._links.redirect.href})
    return JsonResponse({'status': 'error', 'message': 'POST method required.'}, status=405)
    
