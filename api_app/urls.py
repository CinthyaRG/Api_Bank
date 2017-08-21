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
    url(
        r'^ajax/send-transfer/$',
        send_transfer,
        name='send_transfer'),
    url(
        r'^ajax/status-product/$',
        status_product,
        name='status_product'),
    url(
        r'^ajax/get-product/$',
        get_product,
        name='get_product'),
]
