"""tams_node URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from django.urls.conf import include
from webapp.views import attendance_records, dashboard, download_attendance, end_attendance_session
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('attendance/', attendance_records, name='attendance'),
    path('admin/', admin.site.urls),
    path('accounts/profile/', dashboard, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('session/<int:pk>/', download_attendance, name="download"),
    path('session/<int:pk>/end/', end_attendance_session, name="end_session"),
]
