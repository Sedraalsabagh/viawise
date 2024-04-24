"""
URL configuration for Agency project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
#from flights.urls import urlpatterns as flights_urls
from rest_framework_simplejwt.tokens import AccessToken
from django.conf.urls.static import static
from django.conf import settings
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    
    path('flight/',include("flights.urls")),
    path('account/',include('account.urls')),
    path('booking/',include('booking.urls')),

    path('api/token/',TokenObtainPairView.as_view()),
    path('admin/', admin.site.urls),
    #path('', HomePageView.as_view(), name='home'),
    
]
#urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    

