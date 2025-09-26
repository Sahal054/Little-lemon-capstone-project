from django.urls import path
from restaurant import views
#import obtain_auth_token view
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns =[
    path('', views.index, name='index'),
    path('menu/',views.MenuItemsView.as_view(),name='menu'),
    path('menu/<int:pk>',views.SingleMenuItemView.as_view()),
    path('api-token-auth/', obtain_auth_token)
]