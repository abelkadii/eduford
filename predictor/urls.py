from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = []

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

app_name = "predictor"
urlpatterns = [
    path('', views.home, name="home"),
    path('send_data/', views.send_data, name="send_data"),
    path('update/', views.update, name="update"),
    path('locate/', views.locate, name="locate"),
    path('medic/', views.medic, name="medic"),
    path('displaymedic/', views.displaymedic, name="displaymedic"),
    path('get-report/<int:id>', views.getReport, name="getReport"),
    path('report/<uuid>', views.report, name="report"),
]
     