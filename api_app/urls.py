from django.conf.urls import url
from api_app.views import *

urlpatterns = [
    url(
        r'^ajax/validate_data/$',
        validate_data,
        name='validate_data'),
]