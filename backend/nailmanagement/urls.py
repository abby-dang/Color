"""
URL configuration for nailmanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from nailmanagement.app.api.auth import register as account_register
from nailmanagement.app.api.auth import sign_in, sign_out
from nailmanagement.app.api.shops import get_shop_info, get_shops, get_shop_commission_total, update_shop_info, get_shop_services, get_shop_skills, get_shop_appointments, register as shop_register

BASE_URL = "api/auth"

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f"{BASE_URL}/register/", account_register),
    path(f"{BASE_URL}/login/", sign_in),
    path(f"{BASE_URL}/logout/", sign_out),

    #shop registration
    path(f"{BASE_URL}/shop_registration/", shop_register),

    #shop information
    path(f"{BASE_URL}/shops/<int:owner_id>/", get_shops),
    path(f"{BASE_URL}/shop_information/<int:shop_id>/", get_shop_info),
    path(f"{BASE_URL}/update_shop_info/<int:shop_id>/", update_shop_info),
    path(f"{BASE_URL}/shop_commissions/<int:shop_id>/", get_shop_commission_total),
    path(f"{BASE_URL}/shop_services/<int:shop_id>/", get_shop_services),
    path(f"{BASE_URL}/shop_skills/<int:shop_id>/", get_shop_skills),
    path(f"{BASE_URL}/shop_appointments/<int:shop_id>/", get_shop_appointments),
]
