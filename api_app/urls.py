from django.conf.urls import url
from api_app.views import *

urlpatterns = [
    url(
        r'^ajax/validate_data/$',
        validate_data,
        name='validate_data'),
    url(
        r'^ajax/validate_data_forgot/$',
        validate_data_forgot,
        name='validate_data_forgot'),
    url(
        r'^ajax/data-customer/$',
        data_customer,
        name='data_customer'),
]
