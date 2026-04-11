from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = []

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

app_name = "study"
urlpatterns = [
    path('', views.index, name="index"),
    path('load_map/', views.load_map, name="load_map"),
    path('search/', views.search, name="search"),
]
     