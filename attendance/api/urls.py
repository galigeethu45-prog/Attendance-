from django.urls import path
from .views import login_api, register_api, missing_checkouts_api, assign_missing_checkouts_api

urlpatterns = [
    path('login/', login_api),
    path('register/', register_api),
    path('missing-checkouts/', missing_checkouts_api),
    path('assign-missing-checkouts/', assign_missing_checkouts_api),
]