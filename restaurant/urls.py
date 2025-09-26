from django.urls import path, include
from restaurant import views
from rest_framework.routers import DefaultRouter
#import obtain_auth_token view
from rest_framework.authtoken.views import obtain_auth_token

# Create router for ViewSet-based views
router = DefaultRouter()
router.register(r'api/bookings', views.BookingViewSet, basename='api-bookings')
router.register(r'api/users', views.UserViewSet, basename='api-users')

urlpatterns =[
    # Template views (web interface)
    path('', views.IndexView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('book/', views.BookView.as_view(), name='book'),
    path('my-bookings/', views.MyBookingsView.as_view(), name='my-bookings'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # API endpoints
    path('api/menu-items/', views.MenuItemsView.as_view(), name='api-menu-items'),
    path('api/menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='api-menu-item-detail'),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
] + router.urls