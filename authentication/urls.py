from django.contrib import admin
from django.urls import path, include
from . import views
# urls.py

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your other patterns ...
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
app_name = "authentication"

urlpatterns = [
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('verify', views.verify_email, name="verify"),
    path('send_otp', views.send_verification_page, name="send_otp"),

]


     