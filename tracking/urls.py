from django.urls import path
from .views import tracking_code_list

urlpatterns = [
    path('api/tracking-codes/', tracking_code_list, name='tracking-code-list'),
]
