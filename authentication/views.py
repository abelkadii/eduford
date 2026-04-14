from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser as User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from eduford import settings
# from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
import threading
from django.http import JsonResponse
from . tokens import generate_token
import random, json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def threaded(f):
    def wrapper(*args, **kwargs):
        t = threading.Thread(target = f, args = args, kwargs=kwargs)
        t.start()
    return wrapper

@threaded
def welcome_user(myuser):
    subject = "Welcome to Eduford"
    message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Eduford!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\n\nThe Eduford Team."        
    from_email = settings.EMAIL_HOST_USER
    to_list = [myuser.email]
    send_mail(subject, message, from_email, to_list, fail_silently=True)
    # Email Address Confirmation Email

@threaded
def send_verification_email(request, myuser, _redirecting, otp, uid, token):
    email_subject = "Confirm you Eduford Account, Your OTP is: {}".format(otp)
    scheme = request.scheme
    host = request.get_host()
    conf_url = f"{scheme}://{host}/activate/{uid}/{token}"
    if _redirecting:
        conf_url+="?redirect=_redirecting"
    message2 = render_to_string('authentication/email_confirmation.html',{
        'name': myuser.first_name,
        'confirmation_url': conf_url,
        "otp": otp
    })
    email = EmailMessage(
    email_subject,
    message2,
    settings.EMAIL_HOST_USER,
    [myuser.email],
    )
    email.fail_silently = True
    email.send()



def signup(request):
    if request.user.is_authenticated and request.user.email_verified:
        return redirect('core:index')
    if request.method == "POST":
        _redirecting = "redirect=_redirecting" in request.get_full_path()
        as_json = "json=1" in request.get_full_path()

        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            if as_json:
                return JsonResponse({"status": "error", "message": "Username already exist! Please try some other username."})

            messages.error(request, "Username already exist! Please try some other username.")
            if _redirecting:
                return redirect('/signup?redirect=_redirecting')    
            return redirect('authentication:signup')
        
        if User.objects.filter(email=email).exists():
            if as_json:
                return JsonResponse({"status": "error", "message": "Email Already Registered!!"})
            messages.error(request, "Email Already Registered!!")
            if _redirecting:
                return redirect('/signup?redirect=_redirecting')    
            return redirect('authentication:signup')
        
        if len(username)>20:
            if as_json:
                return JsonResponse({"status": "error", "message": "Username must be under 20 charcters!!"})
            messages.error(request, "Username must be under 20 charcters!!")
            if _redirecting:
                return redirect('/signup?redirect=_redirecting')    
            return redirect('authentication:signup')
        
        if pass1 != pass2:
            if as_json:
                return JsonResponse({"status": "error", "message": "Passwords did not matched!!"})
            messages.error(request, "Passwords did not matched!!")
            if _redirecting:
                return redirect('/signup?redirect=_redirecting')    
            return redirect('authentication:signup')
        
        
        myuser = User.objects.create_user(username, email, pass1)
        user = authenticate(request, username=username, password=pass1)
        login(request, user)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.email_verified = False
        # myuser.email_verified = True
        myuser.save()
        # messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
        welcome_user(myuser)
        
        # messages.success(request, "Email has been sent to your email address!! Please confirm your email address to activate your account.")
        send_verification(request, _redirecting)
        if as_json:
                return JsonResponse({"status": "success", "message": "please activate your email"})
        if _redirecting:
            return redirect('/verify?redirect=_redirecting')
        return redirect('/verify')
        
    elif request.method == 'GET':
        rd = request.GET.get('redirect', None)
        context = {"_redirecting": rd=="_redirecting", 'location': 'signup'}
        return render(request, "authentication/signup.html", context)


def activate(request,uidb64,token):
    try:
        _redirecting = request.GET.get('redirect', None) == "_redirecting"
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.email_verified = True
        # user.profile.signup_confirmation = True
        myuser.save()
        messages.success(request, "Your Account has been activated!!")
        if _redirecting:
            return redirect('/signin?redirect=_redirecting')
        return redirect('authentication:signin')
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.user.is_authenticated and request.user.email_verified:
        if request.GET.get('redirect', None) == '_redirecting':
            return redirect('https://store.breathcure.com/default.asp')
        return redirect('core:index')
    if request.method == 'POST':
        _redirecting = "redirect=_redirecting" in request.get_full_path()
        as_json = "json=1" in request.get_full_path()
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = User.objects.filter(username=username).first()
        user = authenticate(username=username, password=pass1)

        if user is not None and not user.email_verified:
            login(request, user)
            if as_json:
                return JsonResponse({"status": "error", "message": "please activate your email"})
            # messages.error(request, "Your Account is not activated!! Please check your email to activate your account.")
            if _redirecting:
                return redirect('/verify?redirect=_redirecting')
            return redirect('/verify')
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            if as_json:
                return JsonResponse({"status": "success", "message": "", "url": "https://store.breathcure.com/default.asp"})
            if request.GET.get('redirect', None) == "_redirecting":
                return redirect('https://store.breathcure.com/default.asp')
            # messages.success(request, "Logged In Sucessfully!!")
            return redirect('core:index')
        else:
            if as_json:
                return JsonResponse({"status": "error", "message": "Bad Credentials!!"})
            context = {
                "redirecting": _redirecting,
                "location": "signin",
                "entered_username": username,
                "login_error": "Username or password is wrong.",
            }
            return render(request, "authentication/login.html", context, status=401)
    elif request.method == 'GET':
        rd = request.GET.get('redirect', None)
        context = {
            "redirecting": rd=="_redirecting",
            "location": "signin",
            "entered_username": "",
        }
        return render(request, "authentication/login.html", context)


def signout(request):
    logout(request)
    # messages.success(request, "Logged Out Successfully!!")
    return redirect('core:index')

def generate_otp():
    return "".join([random.choice("0123456789") for i in range(6)])

# Function to send OTP via email


# View to handle email verification

def send_verification(request, _redirecting):
    email = request.user.email
    otp = generate_otp()
    # Save the OTP to the database
    request.session['email_verification_otp'] = otp
    request.session['email_verification_email'] = email
    # Send the OTP via email
    uid = urlsafe_base64_encode(force_bytes(request.user.pk))
    token = generate_token.make_token(request.user)
    send_verification_email(request, request.user, _redirecting, otp, uid, token)

def send_verification_page(request):
    if not request.user.is_authenticated:
        return redirect('authentication:signin')
    if request.user.email_verified:
        return redirect('core:index')
    
    _redirecting = request.GET.get('redirect', None) == "_redirecting"
    send_verification(request, _redirecting)
    email_without_domain = request.user.email.split("@")[0]
    email = email_without_domain[:3]+"*"*(len(email_without_domain)-4)+email_without_domain[-1] + "@" + request.user.email.split("@")[1]
    return JsonResponse({'status': 'success', 'email': email})
@csrf_exempt
def verify_email(request):
    if not request.user.is_authenticated:
        return redirect('authentication:signin')
    if request.user.email_verified:
        return redirect('core:index')
    if request.method == 'GET':
        email = request.user.email
        _redirecting = request.GET.get('redirect', None) == "_redirecting"
        context = {'email': email, '_redirecting': _redirecting}
        # return redirect('enter_otp_page')
        return render(request, 'authentication/enter_otp.html', context)

    if request.method == 'POST':
        _redirecting = "redirect=_redirecting" in request.get_full_path()
        as_json = "json=1" in request.get_full_path()
        user_entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('email_verification_otp')
        if user_entered_otp == stored_otp:
            # OTP verification successful
            email = request.session.get('email_verification_email')
            # Mark the email as verified in your database
            # For example: user = User.objects.get(email=email)
            request.user.email_verified = True
            request.user.save()
            if as_json:
                return JsonResponse({"status": "success", "message": "", "url": "https://store.breathcure.com/default.asp"})
            if _redirecting:
                return redirect('https://store.breathcure.com/default.asp')
            return redirect('authentication:signin')
        else:
            # Invalid OTP
            
            if as_json:
                return JsonResponse({"status": "error", "message": "Wrong OTP, try again"})
            messages.error(request, "Wrong OTP, try again")
            if _redirecting:
                return redirect("/verify?redirect=_redirecting")
            return redirect("authentication:verify")
    else:
        return render(request, 'authentication/enter_otp.html')
