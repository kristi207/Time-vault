from django.urls import path
from vaultapp import views


urlpatterns = [
    
    path('', views.posts_list),
]