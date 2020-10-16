"""teamwork URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, re_path
import announcement.views as announcement_view
from django.views.static import serve
from teamwork import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', announcement_view.home, name='home'),
    path('home/', announcement_view.home, name='home'),
    path('register/', announcement_view.register, name='register'),
    path('login/', announcement_view.login, name='login'),
    path('check_username_validate/', announcement_view.check_username_validate, name='check_username_validate'),
    path('check_password_validate/', announcement_view.check_password_validate, name='check_password_validate'),
    path('check_lastname_validate/', announcement_view.check_lastname_validate, name='check_lastname_validate'),
    path('check_firstname_validate/', announcement_view.check_firstname_validate, name='check_firstname_validate'),
    path('check_teamname_validate/', announcement_view.check_teamname_validate, name='check_teamname_validate'),
    re_path('^announcement/(.{32})/(\d+)$', announcement_view.make_announcement),
    re_path('^readconfirm/(\d+)/(.*)$', announcement_view.read_confirm, name='read_confirm'),
    re_path('^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path('^showupload/(\d+)/(.*)$', announcement_view.show_upload, name='show_upload'),
    re_path('^feedbackconfirm/(\d+)$', announcement_view.feedback_confirm, name='feedback_confirm'),
]
