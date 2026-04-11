from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = []

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

app_name="shop"
urlpatterns = [
    path('', views.index, name="index"),
    path('products', views.get_products, name="products"),
    path('buy', views.buy, name="buy"),
]
     