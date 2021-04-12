from django.contrib import admin
from django.urls import path, include

from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('', include('BscFront.urls')),
    path('api/', include('analBsc.urls')),
    path('admin/', admin.site.urls),

    path('auth/', include('djoser.urls.authtoken')),

]

urlpatterns += doc_urls
