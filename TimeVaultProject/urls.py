"""
URL configuration for TimeVaultProject project.

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
from django.urls import path,include
from django.conf import  settings
from django.conf.urls.static import static
from vaultapp import views
from vaultapp.views import *
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls, name= 'admin'),
    path('', home, name= 'home'),
    path('about/',about, name= 'about'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('posts/', views.post_list, name='post_list'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('post/<int:id>/add-reaction/', views.add_reaction, name='add_reaction'),
    path('post/<int:id>/add-comment/', views.add_comment, name='add_comment'),
    path('signup/', views.signup, name='signup'), 
    path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('home/', views.home, name='home'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('write-letter/', views.write_letter, name='write_letter'),
    path('write-letter/vaultapp/signin.html', views.signup, name='signup'),
    path('write-letter/vaultapp/letter_scheduled.html', views.letter_scheduled, name='letter_scheduled'),
    path('post/<int:id>/', views.BlogPost, name='post_detail'),
   # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
   



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
