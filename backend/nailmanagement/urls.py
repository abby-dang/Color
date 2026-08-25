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
from nailmanagement.app.api.shop_services import add_service, get_shop_services, remove_shop_service, update_shop_service
from nailmanagement.app.api.auth import register as account_register
from nailmanagement.app.api.auth import sign_in, sign_out
from nailmanagement.app.api.shops import get_shop_info, get_owner_shops, get_shop_commission_total, update_shop_info, get_shop_appointments, register as shop_register
from nailmanagement.app.api.skills import add_skill, get_skills, get_skills_by_name

BASE_URL = "api"
AUTH_BASE_URL = f"{BASE_URL}/auth"
SHOP_BASE_URL = f"{BASE_URL}/shops"
SKILL_BASE_URL = f"{BASE_URL}/skills"
urlpatterns = [
    path('admin/', admin.site.urls),
    path(f"{AUTH_BASE_URL}/register/", account_register),
    path(f"{AUTH_BASE_URL}/login/", sign_in),
    path(f"{AUTH_BASE_URL}/logout/", sign_out),

    #shop registration
    path(f"{SHOP_BASE_URL}/register/", shop_register),

    #shop information
    path(f"{SHOP_BASE_URL}/owner/<int:owner_id>/", get_owner_shops),
    path(f"{SHOP_BASE_URL}/information/<int:shop_id>/", get_shop_info),
    path(f"{SHOP_BASE_URL}/update/<int:shop_id>/", update_shop_info),
    path(f"{SHOP_BASE_URL}/commissions/<int:shop_id>/", get_shop_commission_total),
    path(f"{SHOP_BASE_URL}/appointments/<int:shop_id>/date/<str:day>/", get_shop_appointments),

    #services
    path(f"{SHOP_BASE_URL}/<int:shop_id>/services/add/", add_service),
    path(f"{SHOP_BASE_URL}/<int:shop_id>/services/", get_shop_services),
    path(f"{SHOP_BASE_URL}/<int:shop_id>/services/remove/<int:service_id>/", remove_shop_service),
    path(f"{SHOP_BASE_URL}/<int:shop_id>/services/update/<int:service_id>/", update_shop_service),

    #skills
    path(f"{SKILL_BASE_URL}/add/", add_skill),
    path(f"{SKILL_BASE_URL}/", get_skills),
    path(f"{SKILL_BASE_URL}/name/<str:name>/", get_skills_by_name)
    ]
