"""
URL configuration for littlelemon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from restaurant.views import BookingAPIViewSet, UserViewSet

# API router for DRF ViewSets
router = DefaultRouter()
router.register(r'booking', BookingAPIViewSet, basename='main-booking')
router.register(r'users', UserViewSet, basename='main-users')

# Custom Djoser URL patterns (excluding login and logout to prevent conflicts)
from djoser.urls import urlpatterns as djoser_urlpatterns
from djoser.urls.authtoken import urlpatterns as djoser_token_urlpatterns

# Filter out login and logout endpoints from Djoser to use our custom ones
filtered_djoser_urls = [url for url in djoser_urlpatterns if not any(pattern in str(url.pattern) for pattern in ['login', 'logout'])]
filtered_token_urls = [url for url in djoser_token_urlpatterns if not any(pattern in str(url.pattern) for pattern in ['login', 'logout'])]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurant.urls')),  # Our custom web interface comes FIRST
    path('api/', include(router.urls)),    # API endpoints are under /api/
    path('auth/', include(filtered_djoser_urls)),  # Djoser API endpoints (no logout)
    path('auth/', include(filtered_token_urls)),   # Token auth (no logout)
]

# Serve media files during development and production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
