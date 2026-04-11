from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = []

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

app_name = "pc"
urlpatterns = [
    path('products', views.home, name="products"),
    path('search', views.products, name="search"),
    path('product/<int:id>/<name>', views.product, name="product"),
]
     