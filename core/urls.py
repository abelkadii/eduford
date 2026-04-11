from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = []

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

app_name = "core"
urlpatterns = [
    path('', views.index, name="index"),
    path('about', views.about, name="about"),
    path('blog', views.blog, name="blog"),
    path('contact', views.contact, name="contact"),
    # path('course', views.course, name="course"),
    path('book', views.book, name="book")
]
     